# ArchiMate 3.2 Metamodel — Skill Reference

## Purpose

This file grounds every agent that authors or validates ArchiMate models in the
official element set and relationship rules, so that no agent invents an
element type or a relationship that does not exist in the standard.

## Scope

Covers the Motivation, Strategy, Business, Application, and Technology layers,
as required for the MVP. The Physical layer and the Implementation & Migration
layer, along with the composite elements (Grouping, Location), are not covered
here. If agents need to model those, a follow-up skill file should be produced
using the same method as this one.

## Status

Draft. Requires sign-off from someone with ArchiMate/EA expertise before Epic E
begins. If no one on the team currently holds that expertise, this needs to be
flagged to the client/consultant side and treated as a blocker.

Two parts of this file are not direct spec transcription and need particular
attention during review:

1. The aspect classification in Section 2 (Active Structure / Behavior /
   Passive Structure) was cross-checked against the client-provided training
   deck rather than built element-by-element from the specification text.
2. The relationship-validity matrix in Section 4 is built from the general
   derivation rules described in the specification (Chapter 5, "Relationships
   and Relationship Connectors") together with the relationship definitions
   themselves. It is not copied from the specification's Appendix B, which
   contains the full pairwise relationship tables used for tool
   implementation. Appendix B could not be accessed while preparing this file
   (the Open Group site blocks automated access to that page). Where Section 4
   and Appendix B could disagree on an edge case, Appendix B is the source of
   truth — see Section 6.

---

## 1. Sources

| Source | Description | Used for |
|---|---|---|
| Open Group ArchiMate 3.2 Specification Reference Cards (PDF) | opengroup.org/sites/default/files/docs/downloads/n221p.pdf | Element definitions (Section 2), relationship-type definitions (Section 3) |
| Open Group ArchiMate 3.2 Specification, overview page | pubs.opengroup.org/architecture/archimate3-doc/ | Confirms the service-orientation / realization pattern across the Business, Application, and Technology layers (quoted in Section 4) |
| Open Group ArchiMate 3.2 Specification, Appendix B ("Relationships — Normative") | pubs.opengroup.org/architecture/archimate3-doc/ch-relationships-Normative.html | Authoritative pairwise relationship tables. Not accessible while preparing this file; every place this file relies on the general rule instead of Appendix B is flagged |
| Client training deck, ArchiMate Adoption (7Bots) | Internal | Cross-check for element groupings and the Active Structure / Behavior / Passive Structure classification |
| Client workbook, ArchiMate Framework | Internal | Cross-check for element groupings |

---

## 2. Element Type Tables

Each table lists the element, a one-line definition, and its aspect (Active
Structure, Behavior, Passive Structure, Motivation, or Strategy). Aspect is
what drives relationship legality in Section 4.

### 2.1 Motivation Layer

| Element | Definition | Aspect |
|---|---|---|
| Stakeholder | The role of an individual, team, or organization (or classes thereof) that represents their interests in the effects of the architecture. | Motivation |
| Driver | An external or internal condition that motivates an organization to define its goals and implement the changes necessary to achieve them. | Motivation |
| Assessment | The result of an analysis of the state of affairs of the enterprise with respect to some driver. | Motivation |
| Goal | A high-level statement of intent, direction, or desired end state for an organization and its stakeholders. | Motivation |
| Outcome | An end result, effect, or consequence of a certain state of affairs. | Motivation |
| Principle | A statement of intent defining a general property that applies to any system in a certain context in the architecture. | Motivation |
| Requirement | A statement of need defining a property that applies to a specific system as described by the architecture. | Motivation |
| Constraint | A limitation on aspects of the architecture, its implementation process, or its realization. | Motivation |
| Meaning | The knowledge or expertise present in, or the interpretation given to, a concept in a particular context. | Motivation |
| Value | The relative worth, utility, or importance of a concept. | Motivation |

### 2.2 Strategy Layer

| Element | Definition | Aspect |
|---|---|---|
| Resource | An asset owned or controlled by an individual or organization. | Structure — can be active or passive depending on the resource; confirm default treatment with SME |
| Capability | An ability that an active structure element, such as an organization, person, or system, possesses. | Behavior |
| Value Stream | A sequence of activities that create an overall result for a customer, stakeholder, or end user. | Behavior |
| Course of Action | An approach or plan for configuring some capabilities and resources of the enterprise, undertaken to achieve a goal. | Behavior |

### 2.3 Business Layer

| Element | Definition | Aspect |
|---|---|---|
| Business Actor | A business entity that is capable of performing behavior. | Active Structure |
| Business Role | The responsibility for performing specific behavior, to which an actor can be assigned, or the part an actor plays in a particular action or event. | Active Structure |
| Business Collaboration | An aggregate of two or more business internal active structure elements that work together to perform collective behavior. | Active Structure |
| Business Interface | A point of access where a business service is made available to the environment. | Active Structure |
| Business Process | A sequence of business behaviors that achieves a specific result such as a defined set of products or business services. | Behavior |
| Business Function | A collection of business behavior based on a chosen set of criteria, closely aligned to an organization, but not necessarily explicitly governed by the organization. | Behavior |
| Business Interaction | A unit of collective business behavior performed by (a collaboration of) two or more business actors, roles, or collaborations. | Behavior |
| Business Event | A business-related state change. | Behavior |
| Business Service | Explicitly defined behavior that a business role, actor, or collaboration exposes to its environment. | Behavior |
| Business Object | A concept used within a particular business domain. | Passive Structure |
| Contract | A formal or informal specification of an agreement between a provider and a consumer that specifies the rights and obligations associated with a product. | Passive Structure |
| Representation | A perceptible form of the information carried by a business object. | Passive Structure |
| Product | A coherent collection of services and/or passive structure elements, accompanied by a contract, offered as a whole to internal or external customers. | Passive Structure |

### 2.4 Application Layer

| Element | Definition | Aspect |
|---|---|---|
| Application Component | An encapsulation of application functionality aligned to implementation structure, which is modular and replaceable. | Active Structure |
| Application Collaboration | An aggregate of two or more application internal active structure elements that work together to perform collective application behavior. | Active Structure |
| Application Interface | A point of access where application services are made available to a user, another application component, or a node. | Active Structure |
| Application Function | Automated behavior that can be performed by an application component. | Behavior |
| Application Interaction | A unit of collective application behavior performed by (a collaboration of) two or more application components. | Behavior |
| Application Process | A sequence of application behaviors that achieves a specific result. | Behavior |
| Application Event | An application state change. | Behavior |
| Application Service | An explicitly defined exposed application behavior. | Behavior |
| Data Object | Data structured for automated processing. | Passive Structure |

### 2.5 Technology Layer

| Element | Definition | Aspect |
|---|---|---|
| Node | A computational or physical resource that hosts, manipulates, or interacts with other computational or physical resources. | Active Structure |
| Device | A physical IT resource upon which system software and artifacts may be stored or deployed for execution. | Active Structure |
| System Software | Software that provides or contributes to an environment for storing, executing, and using software or data deployed within it. | Active Structure |
| Technology Collaboration | An aggregate of two or more technology internal active structure elements that work together to perform collective technology behavior. | Active Structure |
| Technology Interface | A point of access where technology services offered by a technology internal active structure element can be accessed. | Active Structure |
| Path | A link between two or more technology internal active structure elements, through which these elements can exchange data, energy, or material. | Active Structure |
| Communication Network | A set of structures and behaviors that connects devices or system software for transmission, routing, and reception of data. | Active Structure |
| Technology Function | A collection of technology behavior that can be performed by a technology internal active structure element. | Behavior |
| Technology Process | A sequence of technology behaviors that achieves a specific result. | Behavior |
| Technology Interaction | A unit of collective technology behavior performed by (a collaboration of) two or more technology internal active structure elements. | Behavior |
| Technology Event | A technology state change. | Behavior |
| Technology Service | An explicitly defined exposed technology behavior. | Behavior |
| Artifact | A piece of data that is used or produced in a software development process, or by deployment and operation of an IT system. | Passive Structure |

---

## 3. Relationship Types

All 11 ArchiMate relationship types, with definitions taken directly from the
specification.

| Category | Relationship | Definition |
|---|---|---|
| Structural | Composition | Represents that an element consists of one or more other concepts. |
| Structural | Aggregation | Represents that an element combines one or more other concepts. |
| Structural | Assignment | Represents the allocation of responsibility, performance of behavior, storage, or execution. |
| Structural | Realization | Represents that an element plays a critical role in the creation, achievement, sustenance, or operation of a more abstract element. |
| Dependency | Serving | Represents that an element provides its functionality to another element. |
| Dependency | Access | Represents the ability of behavior and active structure elements to observe or act upon passive structure elements. |
| Dependency | Influence | Represents that an element affects the implementation or achievement of some motivation element. |
| Dynamic | Triggering | Represents a temporal or causal relationship between elements. |
| Dynamic | Flow | Represents transfer from one element to another. |
| Other | Specialization | Represents that an element is a particular kind of another element. |
| Other | Association | Represents an unspecified relationship, or one that is not represented by another ArchiMate relationship. |

The specification also states that the language uses service-orientation to
distinguish and relate the Business, Application, and Technology layers, and
uses realization relationships to relate concrete elements to more abstract
elements across these layers. This is the core pattern behind most legal
cross-layer relationships in Section 4: Serving connects a layer to the
layer(s) above it that it supports, and Realization connects a concrete or
internal element to a more abstract or exposed element, often but not always
across a layer boundary.

---

## 4. Relationship-Validity Matrix

### 4.1 Legal source/target aspect combinations

This is the general derivation-rule level, not the full Appendix B pairwise
table — see the note at the top of this file. Read each row as: this
relationship may run from an element of the listed source aspect to an
element of the listed target aspect.

| Relationship | Legal source aspect(s) | Legal target aspect(s) | Same layer only |
|---|---|---|---|
| Composition | Active Structure, Passive Structure, Behavior | Same aspect as source | Usually |
| Aggregation | Active Structure, Passive Structure, Behavior | Same aspect as source | Usually |
| Assignment | Active Structure | Behavior, Active Structure, or (Technology layer only) Passive Structure | Usually |
| Realization | Any (Active Structure, Behavior, Passive Structure) | A more abstract counterpart element — often the behavior/service element one layer up, or a Motivation/Strategy element | No, cross-layer is the common case |
| Serving | Active Structure, Behavior | Active Structure, Behavior | No, cross-layer is the common case |
| Access | Behavior, occasionally Active Structure | Passive Structure | Usually |
| Influence | Any element | Motivation element | No, always cross-layer into Motivation |
| Triggering | Behavior | Behavior | No, cross-layer allowed |
| Flow | Behavior | Behavior | No, cross-layer allowed |
| Specialization | Any element | Same element type as source | Always |
| Association | Any element | Any element | No restriction — universal fallback |

### 4.2 Worked examples

These are confirmed-legal patterns, not an exhaustive list. Each is consistent
with the sources in Section 1; treat pairs not listed here as needing SME
confirmation rather than assuming they are valid or invalid.

| Source | Relationship | Target | Pattern |
|---|---|---|---|
| Business Actor | Assignment | Business Role | Active structure to active structure, same layer |
| Business Role | Assignment | Business Process | Active structure to behavior it performs, same layer |
| Business Process | Realization | Business Service | Concrete behavior to exposed behavior, same layer |
| Application Service | Serving | Business Process | Lower layer supports upper layer |
| Application Component | Realization | Application Service | Concrete structure's behavior to exposed service, same layer |
| Application Component | Assignment | Application Function | Active structure to behavior it performs |
| Application Function | Access | Data Object | Behavior reads or writes passive structure |
| Technology Service | Serving | Application Component | Lower layer supports upper layer |
| Node | Assignment | Artifact | Active structure hosts/deploys passive structure — Technology-layer-specific case |
| Node | Realization | Technology Service | Concrete structure's behavior to exposed service |
| Driver | Influence | Goal | Motivation element affects another motivation element |
| Requirement | Influence | Goal | Motivation element affects another |
| Course of Action | Realization | Capability | Strategy element realizes a more abstract strategy element |
| Capability | Serving | Value Stream | Strategy behavior supports another strategy behavior |
| Business Process | Triggering | Business Process | Sequential/causal, same layer |
| Business Process | Flow | Application Process | Cross-layer transfer of information |

### 4.3 Always-legal fallback

Association is legal between any two elements, in either direction, whenever
no more specific relationship applies. Specialization is legal between any
two elements of the exact same element type, regardless of layer.

---

## 5. Decision Procedure

For use by the validator subagent. Given a proposed source element type,
relationship, and target element type:

1. Look up the source and target element types in Section 2 to get each
   one's layer and aspect.
2. Look up the relationship in Section 4.1 to get its legal source and target
   aspects.
3. Reject if either element's aspect is not in the relationship's legal set.
4. Reject if the relationship requires same layer (Section 4.1, last column
   says "Usually" or "Always") but source and target layers differ, unless
   the pair matches a documented cross-layer exception. The only documented
   exception at present is Assignment from Node to Artifact; flag any other
   cross-layer Assignment for manual review rather than auto-rejecting or
   auto-approving it.
5. If the relationship is Influence, reject unless the target is a
   Motivation element.
6. If the relationship is Specialization, reject unless source and target
   are the same element type.
7. If the relationship is Association, Realization, or Serving, treat the
   list in Section 4.2 as confirmed-legal examples, not an exhaustive list.
   For pairs not in that list, flag as needing SME confirmation rather than
   auto-approving, until Appendix B is obtained and Section 4 is upgraded
   from a general-rule approximation to the full pairwise table.

---

## 6. Open Items

- This file has not been reviewed or signed off by an ArchiMate/EA expert.
  Per the Definition of Done, this blocks Epic E from starting. If no one on
  the team currently has this expertise, it needs to be sourced from the
  client or consultant side.
- Appendix B of the specification (the authoritative pairwise relationship
  tables) could not be accessed while preparing this file, because the Open
  Group site blocks automated access to that page. Anyone with manual or
  licensed access to the specification should pull Appendix B directly and
  replace Section 4 with the literal pairwise tables. Until then, Section 4
  is a general-rule approximation — useful for catching obviously invalid
  combinations, but not guaranteed complete for edge cases.
- The aspect of the Strategy-layer Resource element is left ambiguous in
  Section 2.2. The specification allows Resource to represent either an
  active or a passive asset depending on context; this needs an SME decision
  on how the validator should treat it by default.
- The Physical layer and the Implementation & Migration layer are not
  covered in this file. They are out of scope for the current task, but the
  agents will eventually need them. A follow-up skill file is recommended
  once this one is signed off.

---
## Agent Usage

The Architecture Agent should use this skill as follows:

1. Identify the source and target elements.
2. Determine their layer and aspect.
3. Validate that both elements exist in the official ArchiMate metamodel.
4. Select the most specific valid relationship.
5. Reject unsupported relationships.
6. Request clarification if multiple relationships are possible.
7. Never invent new elements or relationships.

## 7. References

- Open Group ArchiMate 3.2 Reference Cards (PDF): https://www.opengroup.org/sites/default/files/docs/downloads/n221p.pdf
- Open Group ArchiMate 3.2 Specification (home): https://pubs.opengroup.org/architecture/archimate3-doc/
- Open Group ArchiMate 3.2 Specification, Relationships chapter: https://pubs.opengroup.org/architecture/archimate3-doc/ch-Relationships-and-Relationship-Connectors.html
- Open Group ArchiMate 3.2 Specification, Appendix B, normative relationship tables (access-restricted while preparing this file): https://pubs.opengroup.org/architecture/archimate3-doc/ch-relationships-Normative.html
- Client training deck: ArchiMate Adoption – Learning Ver 5 (7Bots), internal
- Client workbook: ArchiMate Framework (3).xlsx, internal