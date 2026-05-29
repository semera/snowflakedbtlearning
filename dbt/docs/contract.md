# Person & Address Raw Event Contract

## Scope

This contract defines two raw event feeds:

- `raw_person` for `person.v1` events
- `raw_address` for `address.v1` events

Each row in a raw table contains one JSON document with an `events` array. A single raw row may contain multiple events.

---

## Event Envelope

Each event has two top-level elements:

- `metadata`
- `data`

Example:

```json
{
  "events": [
    {
      "metadata": {
        "event_id": "7b3b31d4-6df8-4e1f-9f7f-6ec22a7d3f41",
        "type": "person.v1",
        "time": "2026-05-23T12:34:56Z",
        "sequence": 1000,
        "mutation": "insert"
      },
      "data": {
        "person_id": "db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1",
        "pin": "1234567890",
        "first_name": "John",
        "surname": "Doe",
        "date_of_birth": "1980-01-15"
      }
    }
  ]
}
```

---

## Raw Table Rules

### `raw_person`

* Contains only `person.v1` events.
* Mixed event types are not allowed.

### `raw_address`

* Contains only `address.v1` events.
* Mixed event types are not allowed.

---

## Metadata Rules

* `event_id` is a globally unique GUID/string.
* `type` identifies the event type.
* Supported event types:

  * `person.v1`
  * `address.v1`
* `time` is an ISO UTC timestamp.
* `sequence` is an integer.
* `mutation` is one of:

  * `insert`
  * `update`
  * `delete`

---

## Sequencing Rules

* `sequence` is monotonic and gap-less per event type.
* `person.v1` and `address.v1` have independent sequences.
* The first observed sequence does not have to be `1`.
* Delivery order is not guaranteed.
* Events inside one raw row do not have to be ordered by `sequence`.
* Processing order is determined by `sequence`, not by ingest order and not by `time`.
* A gap in sequence means one or more events are missing.
* Missing sequence events may arrive late, even several days later.
* A sequence gap should be ignored temporarily.
* If a gap is still missing after 5 minutes, it should eventually be logged.

---

## Idempotency Rules

* The same `event_id` may appear more than once.
* Duplicate `event_id` may occur:

  * across different raw rows
  * inside the same raw row
* Same `event_id` with the same content is an idempotent duplicate.
* Same `event_id` with different content is an error and should eventually be logged.
* Deduplication may be handled per entity feed, although `event_id` is globally unique.

---

## Mutation Rules

* `insert`, `update`, and `delete` all contain a full hydrated entity state in `data`.
* `data` contains all currently known fields for the entity.
* Optional fields are omitted when unknown or not applicable.
* Optional fields are never represented as `null`.
* `update` contains the new full state.
* `delete` contains the last known full state before deletion.
* `insert` must not appear after an `update` or `delete` for the same entity key in sequence order.
* `update` or `delete` may appear without a previously processed `insert`, because:

  * the consumer may start from a later sequence, or
  * earlier sequence events may not have arrived yet.

---

## Ingestion Rules

* Raw tables are append-only.
* `ingest_timestamp` is generated when the raw JSON is stored.
* No additional source metadata is required for now.

---

## Person Rules

Entity type: `person.v1`

### Required fields

* `person_id`
* `pin`
* `first_name`
* `surname`

### Optional fields

* `date_of_birth`

### Business rules

* `person_id` is a stable unique identifier.
* `person_id` is a GUID/string.
* `pin` is mandatory.
* `pin` may change for the same `person_id`.
* `first_name` is mandatory.
* `surname` is mandatory.
* `date_of_birth` is optional.
* `date_of_birth` is a string in `YYYY-MM-DD` format.

---

## Address Rules

Entity type: `address.v1`

### Required fields

* `address_id`
* `person_id`
* `address_type`
* `city`

### Optional fields

* `street`

### Business rules

* `address_id` is a GUID/string.
* `person_id` is a GUID/string referencing a person.
* An address event may arrive before the corresponding person event.
* This is considered a temporary consistency state.
* `address_type` is an enum:

  * `permanent`
  * `correspondent`
* A person may have at most one current address per `address_type`.
* Historically, a person may have multiple different `address_id` values for the same `address_type`, because an address can be deleted and later recreated with a new ID.
* `city` is mandatory.
* `street` is optional.

---

# JSON Schemas

## 1. Common Raw Event Envelope Schema

This schema validates the shared raw event structure. It does not validate the entity-specific `data` payload.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/schemas/raw-event-envelope.schema.json",
  "title": "Raw Event Envelope",
  "type": "object",
  "required": ["events"],
  "additionalProperties": false,
  "properties": {
    "events": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["metadata", "data"],
        "additionalProperties": false,
        "properties": {
          "metadata": {
            "type": "object",
            "required": ["event_id", "type", "time", "sequence", "mutation"],
            "additionalProperties": false,
            "properties": {
              "event_id": {
                "type": "string",
                "format": "uuid"
              },
              "type": {
                "type": "string",
                "enum": ["person.v1", "address.v1"]
              },
              "time": {
                "type": "string",
                "format": "date-time"
              },
              "sequence": {
                "type": "integer",
                "minimum": 0
              },
              "mutation": {
                "type": "string",
                "enum": ["insert", "update", "delete"]
              }
            }
          },
          "data": {
            "type": "object"
          }
        }
      }
    }
  }
}
```

---

## 2. `person.v1` Data Schema

This schema validates only the `data` object for `person.v1`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/schemas/person-v1-data.schema.json",
  "title": "person.v1 Data",
  "type": "object",
  "required": ["person_id", "pin", "first_name", "surname"],
  "additionalProperties": false,
  "properties": {
    "person_id": {
      "type": "string",
      "format": "uuid"
    },
    "pin": {
      "type": "string",
      "minLength": 1
    },
    "first_name": {
      "type": "string",
      "minLength": 1
    },
    "surname": {
      "type": "string",
      "minLength": 1
    },
    "date_of_birth": {
      "type": "string",
      "format": "date"
    }
  }
}
```

---

## 3. `address.v1` Data Schema

This schema validates only the `data` object for `address.v1`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/schemas/address-v1-data.schema.json",
  "title": "address.v1 Data",
  "type": "object",
  "required": ["address_id", "person_id", "address_type", "city"],
  "additionalProperties": false,
  "properties": {
    "address_id": {
      "type": "string",
      "format": "uuid"
    },
    "person_id": {
      "type": "string",
      "format": "uuid"
    },
    "address_type": {
      "type": "string",
      "enum": ["permanent", "correspondent"]
    },
    "street": {
      "type": "string",
      "minLength": 1
    },
    "city": {
      "type": "string",
      "minLength": 1
    }
  }
}
```
