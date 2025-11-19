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


"""
Data component models for CycloneDX 1.5+.

This module implements the `componentDataType` and related types as defined by the
CycloneDX schema. These are used when a `Component` is of type `data` and allows
describing dataset metadata, contents, and governance.

Notes
-----
- JSON Schema: https://cyclonedx.org/docs/1.7/json/#component_component_data
- XML Schema: https://cyclonedx.org/docs/1.7/xml/#type_componentDataType
- Governance parties are a union of organization or individual (contact).
- The `classification` field in component data is modeled as a string to be
  compatible with the XML XSD. JSON schema references `dataClassification`,
  so this field is optional in our model to avoid cross-format conflicts.
"""

from collections.abc import Iterable
from enum import Enum
from typing import Any, Optional

import py_serializable as serializable
from sortedcontainers import SortedSet

from .._internal.compare import ComparableTuple as _ComparableTuple
from ..model import AttachedText, Property, XsUri
from ..model.bom_ref import BomRef
from ..model.contact import OrganizationalContact, OrganizationalEntity
from ..schema.schema import SchemaVersion1Dot5, SchemaVersion1Dot6, SchemaVersion1Dot7
from .model_card import Graphic, GraphicsCollection


@serializable.serializable_enum
class ComponentDataKind(str, Enum):
    """Permissible types for `component.data[*].type`. See XSD `componentDataTypeEnumeration`."""

    SOURCE_CODE = 'source-code'
    CONFIGURATION = 'configuration'
    DATASET = 'dataset'
    DEFINITION = 'definition'
    OTHER = 'other'


@serializable.serializable_class(ignore_unknown_during_deserialization=True)
class DataContents:
    """Contents or references to the contents of the data being described."""

    def __init__(
            self, *,
            attachment: Optional[AttachedText] = None,
            url: Optional[XsUri] = None,
            properties: Optional[Iterable[Property]] = None,
    ) -> None:
        self.attachment = attachment
        self.url = url
        self.properties = properties or []

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_sequence(1)
    def attachment(self) -> Optional[AttachedText]:
        return self._attachment

    @attachment.setter
    def attachment(self, attachment: Optional[AttachedText]) -> None:
        self._attachment = attachment

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_sequence(2)
    def url(self) -> Optional[XsUri]:
        return self._url

    @url.setter
    def url(self, url: Optional[XsUri]) -> None:
        self._url = url

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_sequence(3)
    @serializable.xml_name('properties')
    @serializable.xml_array(serializable.XmlArraySerializationType.NESTED, 'property')
    def properties(self) -> 'SortedSet[Property]':
        return self._properties

    @properties.setter
    def properties(self, properties: Iterable[Property]) -> None:
        self._properties = SortedSet(properties)

    def __comparable_tuple(self) -> _ComparableTuple:
        return _ComparableTuple((self.attachment, self.url, _ComparableTuple(self.properties)))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DataContents):
            return self.__comparable_tuple() == other.__comparable_tuple()
        return False

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, DataContents):
            return self.__comparable_tuple() < other.__comparable_tuple()
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__comparable_tuple())

    def __repr__(self) -> str:
        return f'<DataContents attachment={self.attachment is not None}, url={self.url is not None}>'


@serializable.serializable_class(ignore_unknown_during_deserialization=True)
class DataGovernanceResponsibleParty:
    """Union type for data governance parties: organization or individual (contact)."""

    def __init__(
            self, *,
            organization: Optional[OrganizationalEntity] = None,
            contact: Optional[OrganizationalContact] = None,
    ) -> None:
        self.organization = organization
        self.contact = contact

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_sequence(1)
    def organization(self) -> Optional[OrganizationalEntity]:
        return self._organization

    @organization.setter
    def organization(self, organization: Optional[OrganizationalEntity]) -> None:
        self._organization = organization

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.json_name('contact')
    @serializable.xml_name('individual')
    @serializable.xml_sequence(2)
    def contact(self) -> Optional[OrganizationalContact]:
        return self._contact

    @contact.setter
    def contact(self, contact: Optional[OrganizationalContact]) -> None:
        self._contact = contact

    def __comparable_tuple(self) -> _ComparableTuple:
        return _ComparableTuple((self.organization, self.contact))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DataGovernanceResponsibleParty):
            return self.__comparable_tuple() == other.__comparable_tuple()
        return False

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, DataGovernanceResponsibleParty):
            return self.__comparable_tuple() < other.__comparable_tuple()
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__comparable_tuple())

    def __repr__(self) -> str:
        return f'<DataGovernanceResponsibleParty org={self.organization is not None} contact={self.contact is not None}>'


@serializable.serializable_class(ignore_unknown_during_deserialization=True)
class DataGovernance:
    """Governance information: custodians, stewards, and owners."""

    def __init__(
            self, *,
            custodians: Optional[Iterable[DataGovernanceResponsibleParty]] = None,
            stewards: Optional[Iterable[DataGovernanceResponsibleParty]] = None,
            owners: Optional[Iterable[DataGovernanceResponsibleParty]] = None,
    ) -> None:
        self.custodians = custodians or []
        self.stewards = stewards or []
        self.owners = owners or []

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_name('custodians')
    @serializable.xml_array(serializable.XmlArraySerializationType.NESTED, 'custodian')
    @serializable.xml_sequence(1)
    def custodians(self) -> 'SortedSet[DataGovernanceResponsibleParty]':
        return self._custodians

    @custodians.setter
    def custodians(self, custodians: Iterable[DataGovernanceResponsibleParty]) -> None:
        self._custodians = SortedSet(custodians)

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_name('stewards')
    @serializable.xml_array(serializable.XmlArraySerializationType.NESTED, 'steward')
    @serializable.xml_sequence(2)
    def stewards(self) -> 'SortedSet[DataGovernanceResponsibleParty]':
        return self._stewards

    @stewards.setter
    def stewards(self, stewards: Iterable[DataGovernanceResponsibleParty]) -> None:
        self._stewards = SortedSet(stewards)

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_name('owners')
    @serializable.xml_array(serializable.XmlArraySerializationType.NESTED, 'owner')
    @serializable.xml_sequence(3)
    def owners(self) -> 'SortedSet[DataGovernanceResponsibleParty]':
        return self._owners

    @owners.setter
    def owners(self, owners: Iterable[DataGovernanceResponsibleParty]) -> None:
        self._owners = SortedSet(owners)

    def __comparable_tuple(self) -> _ComparableTuple:
        return _ComparableTuple((_ComparableTuple(self.custodians), _ComparableTuple(self.stewards), _ComparableTuple(self.owners)))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DataGovernance):
            return self.__comparable_tuple() == other.__comparable_tuple()
        return False

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, DataGovernance):
            return self.__comparable_tuple() < other.__comparable_tuple()
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__comparable_tuple())

    def __repr__(self) -> str:
        return f'<DataGovernance custodians={len(self.custodians)} stewards={len(self.stewards)} owners={len(self.owners)}>'


@serializable.serializable_class(ignore_unknown_during_deserialization=True)
class ComponentData:
    """Implementation of the `componentDataType` structure."""

    def __init__(
            self, *,
            type: ComponentDataKind,
            name: Optional[str] = None,
            contents: Optional[DataContents] = None,
            classification: Optional[str] = None,
            sensitive_data: Optional[Iterable[str]] = None,
            graphics: Optional[GraphicsCollection] = None,
            description: Optional[str] = None,
            governance: Optional[DataGovernance] = None,
            bom_ref: Optional[BomRef | str] = None,
    ) -> None:
        self.type = type
        self.name = name
        self.contents = contents
        self.classification = classification
        self.sensitive_data = sensitive_data or []
        self.graphics = graphics
        self.description = description
        self.governance = governance
        self._bom_ref = BomRef(str(bom_ref)) if isinstance(bom_ref, str) else bom_ref

    @property
    @serializable.json_name('bom-ref')
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.type_mapping(BomRef)
    @serializable.xml_attribute()
    @serializable.xml_name('bom-ref')
    def bom_ref(self) -> Optional[BomRef]:
        return self._bom_ref

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_sequence(1)
    def type(self) -> ComponentDataKind:
        return self._type

    @type.setter
    def type(self, type: ComponentDataKind) -> None:
        self._type = type

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_sequence(2)
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, name: Optional[str]) -> None:
        self._name = name

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_sequence(3)
    def contents(self) -> Optional[DataContents]:
        return self._contents

    @contents.setter
    def contents(self, contents: Optional[DataContents]) -> None:
        self._contents = contents

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_sequence(4)
    def classification(self) -> Optional[str]:
        return self._classification

    @classification.setter
    def classification(self, classification: Optional[str]) -> None:
        self._classification = classification

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.json_name('sensitiveData')
    @serializable.xml_array(serializable.XmlArraySerializationType.FLAT, 'sensitiveData')
    @serializable.xml_sequence(5)
    def sensitive_data(self) -> 'SortedSet[str]':
        return self._sensitive_data

    @sensitive_data.setter
    def sensitive_data(self, sensitive_data: Iterable[str]) -> None:
        self._sensitive_data = SortedSet(sensitive_data)

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_sequence(6)
    def graphics(self) -> Optional[GraphicsCollection]:
        return self._graphics

    @graphics.setter
    def graphics(self, graphics: Optional[GraphicsCollection]) -> None:
        self._graphics = graphics

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_sequence(7)
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, description: Optional[str]) -> None:
        self._description = description

    @property
    @serializable.view(SchemaVersion1Dot5)
    @serializable.view(SchemaVersion1Dot6)
    @serializable.view(SchemaVersion1Dot7)
    @serializable.xml_sequence(8)
    def governance(self) -> Optional[DataGovernance]:
        return self._governance

    @governance.setter
    def governance(self, governance: Optional[DataGovernance]) -> None:
        self._governance = governance

    def __comparable_tuple(self) -> _ComparableTuple:
        return _ComparableTuple((
            self.type, self.name, self.contents, self.classification,
            _ComparableTuple(self.sensitive_data), self.graphics, self.description, self.governance,
            BomRef.serialize(self.bom_ref) if self.bom_ref else None  # type: ignore[attr-defined]
        ))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ComponentData):
            return self.__comparable_tuple() == other.__comparable_tuple()
        return False

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, ComponentData):
            return self.__comparable_tuple() < other.__comparable_tuple()
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__comparable_tuple())

    def __repr__(self) -> str:
        return f'<ComponentData type={self.type} name={self.name!r}>'
