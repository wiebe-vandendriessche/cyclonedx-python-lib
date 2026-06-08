# This file is part of CycloneDX Python Library
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) OWASP Foundation. All Rights Reserved.

from unittest import TestCase
from warnings import warn

from cyclonedx.exception import MissingOptionalDependencyException
from cyclonedx.model import AttachedText, Property, XsUri
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.contact import OrganizationalContact, OrganizationalEntity
from cyclonedx.model.data import (
    ComponentData,
    ComponentDataKind,
    DataContents,
    DataGovernance,
    DataGovernanceResponsibleParty,
)
from cyclonedx.output.json import BY_SCHEMA_VERSION as JSON_BY_SCHEMA_VERSION
from cyclonedx.output.xml import BY_SCHEMA_VERSION as XML_BY_SCHEMA_VERSION
from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator
from cyclonedx.validation.xml import XmlValidator


class TestComponentDataBasic(TestCase):
    def test_component_data_basic_v15_json_xml(self) -> None:
        """Basic component.data in BOM 1.5 JSON and XML."""
        contents = DataContents(
            url=XsUri('https://example.org/dataset.csv'),
            properties=[Property(name='format', value='csv')],
        )
        cd = ComponentData(
            type=ComponentDataKind.DATASET,
            name='example-dataset',
            contents=contents,
            sensitive_data=['PII'],
            description='Sample dataset',
        )
        c = Component(name='my-data', type=ComponentType.DATA, data=[cd])
        bom = Bom(components=[c])

        # JSON 1.5
        json = JSON_BY_SCHEMA_VERSION[SchemaVersion.V1_5](bom).output_as_string(indent=2)
        try:
            err = JsonStrictValidator(SchemaVersion.V1_5).validate_str(json)
        except MissingOptionalDependencyException:
            warn('!!! skipped schema validation', category=UserWarning, stacklevel=0)
        else:
            self.assertIsNone(err, json)
        self.assertIn('"data"', json)
        self.assertIn('"example-dataset"', json)

        # XML 1.5
        xml = XML_BY_SCHEMA_VERSION[SchemaVersion.V1_5](bom).output_as_string(indent=2)
        try:
            errx = XmlValidator(SchemaVersion.V1_5).validate_str(xml)
        except MissingOptionalDependencyException:
            warn('!!! skipped schema validation', category=UserWarning, stacklevel=0)
        else:
            self.assertIsNone(errx, xml)
        self.assertIn('<data>', xml)
        self.assertIn('<name>example-dataset</name>', xml)


class TestComponentDataGovernance(TestCase):
    def test_data_governance_union_v17(self) -> None:
        """Governance supports organization or contact for each party in 1.7."""
        org = OrganizationalEntity(name='DataCorp')
        contact = OrganizationalContact(name='Jane Doe', email='jane@example.org')
        gov = DataGovernance(
            custodians=[DataGovernanceResponsibleParty(organization=org)],
            stewards=[DataGovernanceResponsibleParty(contact=contact)],
            owners=[DataGovernanceResponsibleParty(organization=org)],
        )

        graphic = AttachedText(content='iVBORw0KGgo=', content_type='image/png')
        contents = DataContents(attachment=graphic)

        cd = ComponentData(
            type=ComponentDataKind.CONFIGURATION,
            name='cfg',
            contents=contents,
            governance=gov,
        )
        c = Component(name='cfg-data', type=ComponentType.DATA, data=[cd])
        bom = Bom(components=[c])

        # JSON 1.7
        json = JSON_BY_SCHEMA_VERSION[SchemaVersion.V1_7](bom).output_as_string(indent=2)
        try:
            err = JsonStrictValidator(SchemaVersion.V1_7).validate_str(json)
        except MissingOptionalDependencyException:
            warn('!!! skipped schema validation', category=UserWarning, stacklevel=0)
        else:
            self.assertIsNone(err, json)
        self.assertIn('"custodians"', json)
        self.assertIn('"stewards"', json)
        self.assertIn('"owners"', json)

        # XML 1.7
        xml = XML_BY_SCHEMA_VERSION[SchemaVersion.V1_7](bom).output_as_string(indent=2)
        try:
            errx = XmlValidator(SchemaVersion.V1_7).validate_str(xml)
        except MissingOptionalDependencyException:
            warn('!!! skipped schema validation', category=UserWarning, stacklevel=0)
        else:
            self.assertIsNone(errx, xml)
        self.assertIn('<custodians>', xml)
        self.assertIn('<stewards>', xml)
        self.assertIn('<owners>', xml)

    def test_org_with_contacts_in_governance_v17(self) -> None:
        """Organizations in governance may include contacts; validate JSON/XML 1.7."""
        org_contact = OrganizationalContact(name='Ops Oncall', email='oncall@example.org')
        org = OrganizationalEntity(name='DataCorp', contacts=[org_contact])
        gov = DataGovernance(
            owners=[DataGovernanceResponsibleParty(organization=org)]
        )

        cd = ComponentData(
            type=ComponentDataKind.DATASET,
            name='owners-with-org-contacts',
            governance=gov,
        )
        c = Component(name='data-with-gov', type=ComponentType.DATA, data=[cd])
        bom = Bom(components=[c])

        # JSON 1.7
        json = JSON_BY_SCHEMA_VERSION[SchemaVersion.V1_7](bom).output_as_string(indent=2)
        try:
            err = JsonStrictValidator(SchemaVersion.V1_7).validate_str(json)
        except MissingOptionalDependencyException:
            warn('!!! skipped schema validation', category=UserWarning, stacklevel=0)
        else:
            self.assertIsNone(err, json)
        # organization with nested contact array
        self.assertIn('"owners"', json)
        self.assertIn('"organization"', json)
        self.assertIn('"contact"', json)
        self.assertIn('"Ops Oncall"', json)

        # XML 1.7
        xml = XML_BY_SCHEMA_VERSION[SchemaVersion.V1_7](bom).output_as_string(indent=2)
        try:
            errx = XmlValidator(SchemaVersion.V1_7).validate_str(xml)
        except MissingOptionalDependencyException:
            warn('!!! skipped schema validation', category=UserWarning, stacklevel=0)
        else:
            self.assertIsNone(errx, xml)
        self.assertIn('<owners>', xml)
        self.assertIn('<organization>', xml)
        self.assertIn('<contact>', xml)
        self.assertIn('<name>Ops Oncall</name>', xml)

    def test_mixed_owners_org_with_contacts_and_contact_v17(self) -> None:
        """Owners may include an organization (with contacts) and a standalone contact."""
        org_contact = OrganizationalContact(name='Ops Oncall', email='oncall@example.org')
        org = OrganizationalEntity(name='DataCorp', contacts=[org_contact])
        contact_owner = OrganizationalContact(name='Alice Owner', email='alice.owner@example.org')

        gov = DataGovernance(
            owners=[
                DataGovernanceResponsibleParty(organization=org),
                DataGovernanceResponsibleParty(contact=contact_owner),
            ]
        )

        cd = ComponentData(
            type=ComponentDataKind.DATASET,
            name='mixed-owners',
            governance=gov,
        )
        c = Component(name='data-with-mixed-owners', type=ComponentType.DATA, data=[cd])
        bom = Bom(components=[c])

        # JSON 1.7
        json = JSON_BY_SCHEMA_VERSION[SchemaVersion.V1_7](bom).output_as_string(indent=2)
        try:
            err = JsonStrictValidator(SchemaVersion.V1_7).validate_str(json)
        except MissingOptionalDependencyException:
            warn('!!! skipped schema validation', category=UserWarning, stacklevel=0)
        else:
            self.assertIsNone(err, json)
        # contains owners with both organization and a standalone contact
        self.assertIn('"owners"', json)
        self.assertIn('"organization"', json)
        self.assertIn('"Alice Owner"', json)

        # XML 1.7
        xml = XML_BY_SCHEMA_VERSION[SchemaVersion.V1_7](bom).output_as_string(indent=2)
        try:
            errx = XmlValidator(SchemaVersion.V1_7).validate_str(xml)
        except MissingOptionalDependencyException:
            warn('!!! skipped schema validation', category=UserWarning, stacklevel=0)
        else:
            self.assertIsNone(errx, xml)
        self.assertIn('<owners>', xml)
        self.assertIn('<organization>', xml)
        # standalone contact represented by <individual> in XML
        self.assertIn('<individual>', xml)
        self.assertIn('<name>Alice Owner</name>', xml)
