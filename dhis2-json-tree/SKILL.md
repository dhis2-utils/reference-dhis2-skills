---
name: dhis2-json-tree
description: "Use when writing, reviewing or fixing Java code that reads JSON with json-tree (org.hisp.dhis:json-tree, package org.hisp.dhis.jsontree): JsonMixed, JsonObject, JsonArray, JsonValue, JsonNode, getString(..).string(), bool(), values(Index.SKIP), user-type interfaces extending JsonObject, @Validation. Triggers on dhis2-core input readers and import parsers (data value sets, tracker, metadata, CSV/JSON import), Jackson-to-json-tree migrations, 'accept a number where a string is expected', lenient booleans, missing vs null, streaming large JSON arrays, JsonTreeException / JsonPathException / JsonFormatException, and review feedback like 'these helpers are not needed' or 'json-tree already does that'. Also use before adding any helper method that converts or type-checks a JsonValue."
---

# json-tree for DHIS2 code

## Overview

json-tree is a lazy, virtual JSON tree. Navigation never throws, and the terminal operations (`string()`, `bool()`, `integer()`, `values()` …) are **deliberately lenient**: they return the sensible value for every input that has a reasonable reading, and throw (with the JSON path in the message) only when there is none.

**Core principle: the library's lenient conversions are the contract. Write code as if the value is present and of the right type, and let the terminal operation convert or throw.** Code that checks `type()` before calling `string()`, or writes its own `text()`/`bool()`/`elements()`/`object()` helper, almost always duplicates the library. Reviewers will ask you to delete it (dhis2-core PR #26219: *"Most or all of the 'access as string' helpers should not be needed."*).

This leniency arrived in **json-tree 1.9**. In 1.8.x, `string()` on a number threw. Agents that remember the 1.8 behaviour, or that "don't trust" the coercion, write the defensive helpers. dhis2-core master pins **1.12.0**. Check `dhis-json-tree.version` in `dhis-2/pom.xml`. Everything below was verified on 1.12.0 and 1.14.

## Verified behaviour (1.9+)

`o` is a `JsonObject`. "Missing" means the member is absent. `null` means it is declared JSON `null`.

| Call | string `"x"` | number `5.50` | boolean `true` | missing / `null` | array / object |
|---|---|---|---|---|---|
| `o.getString(k).string()` | `"x"` | `"5.50"` (exact source text) | `"true"` | `null` | throws `JsonTreeException` |
| `o.getString(k).string("d")` | `"x"` | `"5.50"` | `"true"` | `"d"` | throws |
| `o.getBoolean(k).bool()` | `"true"`/`"FALSE"` (any case) → Boolean; other text → `IllegalArgumentException` | throws `JsonTreeException` (also `1`/`0`) | `true` | `null` | throws |
| `o.getBoolean(k).booleanValue(false)` | as `bool()` | throws | `true` | `false` | throws |
| `o.getNumber(k).integer()` | `"12"` → 12; `"x"` → `NumberFormatException` | 5 (cast) | throws | `null` | throws |
| `o.getNumber(k).intValue()` | as above | 5 | throws | **throws `JsonPathException`** | throws |
| `o.getArray(k).values()` | throws | throws | throws | **empty** | array: elements; object: throws |
| `o.getArray(k).stringValues()` | – | – | – | `[]` | `[1,"a",true,null]` → `["1","a","true","null"]` |
| `o.getMap(k, JsonString.class).toMap(JsonString::string)` | throws | throws | throws | `{}` | object: map |
| `o.get(k).toJson()` | `"\"x\""` | `"5.50"` | `"true"` | missing: throws | raw source text |

The `get…` navigation calls never throw, whatever the actual type. `o.get("a").get("b").get("c").string()` returns `null` when any step is missing.

Full matrix, exception types and version history: `references/value-access.md`.

## How to write a reader

1. **Read scalars with the typed terminal op directly.** Use `dv.getString("value").string()` for any scalar-as-text (string, number or boolean), not a `switch (type())`, `node().getDeclaration()` or `node().textValue()`.
2. **Don't guard what the op already handles.** Missing or `null` gives `null`, an empty list or the default. A wrong container type throws a `JsonTreeException` that already names the path (`ARRAY node at path .arr is not a STRING …`). So:
   - `for (JsonMixed e : o.getArray("dataValues").values(Index.SKIP))` needs no `exists()`, `isNull()` or `isArray()` check first.
   - `if (!x.isUndefined()) setter.accept(x.string())` is fine when the setter must not run for absent values. Don't add an `isString()` check.
3. **A strict check in front of a lenient op re-introduces the bug.** `coc.isString() ? coc.string() : null` drops a numeric `123` to null (this was the 2.43 bug). Branch only on the case the op can't serve: `coc.isObject() ? null : coc.string()`.
4. **Add a check only where navigation would silently succeed.** Navigating *through* a primitive yields undefined instead of throwing. `getObject("s").getString("k").string()` is `null` when `s` is `"x"`. A `JsonMixed` element of `[1, {...}]` viewed as an object reads every property as `null`. If a non-object entry must be a 400, check `e.isObject()` once per entry.
5. **A compatibility helper covers only the delta, then delegates.** Probe the library first (step 7). Example: Jackson also accepted `1`/`0` and `""` for booleans; json-tree's `bool()` handles everything else.
   ```java
   /** json-tree bool() plus what Jackson (2.42) also accepted: 1/0, and "" as no value. */
   @CheckForNull
   private static Boolean bool(@Nonnull JsonMixed v) {
     if (v.isNumber()) {
       String n = v.toJson();
       if ("1".equals(n)) return true;
       if ("0".equals(n)) return false;
     }
     if (v.isString() && v.string().isEmpty()) return null;
     return v.bool(); // true/false, "true"/"false" any case, missing/null -> null, else throws
   }
   ```
   A helper that re-implements the cases `bool()`/`string()` already cover is the anti-pattern.
6. **Map the library's exceptions once, at the boundary**, instead of pre-validating every property to produce your own message. In dhis2-core:
   ```java
   } catch (JsonTreeException | JsonPathException | JsonAccessException | IllegalArgumentException ex) {
     // JsonFormatException, JsonSchemaException and NumberFormatException are IllegalArgumentExceptions
     throw new BadRequestException(ErrorCode.E8036, ex.getMessage());
   }
   ```
7. **When unsure what an op does, write the probe test, don't write the helper.** The reviewer settled PR #26219 with a test like this one:
   ```java
   @Test
   void stringIsLenient() {
     assertNull(JsonMixed.of("null").string());
     assertNull(JsonMixed.of("{}").get("undefined").string());
     assertEquals("", JsonMixed.of("\"\"").string());
     assertEquals("123", JsonMixed.of("123").string());
     assertEquals("true", JsonMixed.of("true").string());
     assertThrows(JsonTreeException.class, () -> JsonMixed.of("[]").string());
     assertThrows(JsonTreeException.class, () -> JsonMixed.of("{}").string());
   }
   ```
   Keep that kind of test in the PR: it documents the reliance.

## Missing vs null

| | missing | `"k": null` | `"k": 1` |
|---|---|---|---|
| `o.exists("k")` / `o.get("k").exists()` | false | **true** | true |
| `o.get("k").isNull()` | false | true | false |
| `o.get("k").isUndefined()` | true | true | false |

When missing and `null` mean different things (for example "leave unchanged" vs "clear"), branch on `exists()` and then on `isNull()`. Otherwise use `isUndefined()`, or just the null that `string()` returns.

## Large input and streaming

- json-tree parses lazily from an **in-memory** `char[]`. There is no `InputStream` entry point. `JsonNode.of(byte[], charset, onGet, index)`, `JsonNode.of(Path)` and `JsonMixed.of(CharSequence)` all hold the whole document. Memory stays close to the size of the input because nodes are offsets, not an object graph. dhis2-core's data value import accepts this (`readAllBytes()` then `JsonNode.of(json, UTF_8, null, Index.AUTO_SKIP)`). **Don't write your own JSON tokenizer or splitter** to stream with it. If whole-document memory is really unacceptable, raise it as a design question.
- For a one-pass loop over a big array, use `array.values(Index.SKIP)` (on recent versions `values()` with no argument also uses `SKIP`). Plain `for (x : array)`, `array.stream()` and `getList(..).toList(..)` use `AUTO`, which caches every container element for the life of the tree. Build each element's record and let the view go.
- Laziness means syntax errors surface only where you read. To reject truncated input or trailing junk up front, call `root.node().endIndex()` once. A later broken element otherwise throws `JsonFormatException` mid-loop, after earlier elements were already processed.

## User types instead of hand-mapping

For a reusable shape, declare an interface and view the tree through it:

```java
public interface JsonEvent extends JsonObject {
  default String event() { return getString("event").string(); }
  ImportStrategy importStrategy();        // abstract: member "importStrategy"; enum is lenient ("create-and-update" works)
  LocalDate occurredAt();                 // ISO string -> LocalDate, missing -> null
  Optional<String> note();                // missing -> Optional.empty()
  default boolean completed() { return getBoolean("completed").booleanValue(false); }
  default JsonList<JsonDataValue> dataValues() { return getList("dataValues", JsonDataValue.class); }
}
JsonEvent ev = element.as(JsonEvent.class);  // a view, no copy, no check
```

- Abstract methods map by name (`getX`/`isX` prefixes are stripped). Built-in accessors cover String, boxed and primitive numbers and booleans, BigDecimal/BigInteger, enums, `java.time`, UUID, List/Set/Map/Optional/Stream and records.
- **A primitive return type throws `JsonAccessException` when the member is missing.** Use a `default` method with `booleanValue(false)` / `intValue(0)`, or a boxed type.
- Wrapping `bool()` or `integer()` in a primitive return unboxes `null` into a `NullPointerException` (`default boolean x() { return getBoolean("x").bool(); }`).
- Enums and other types referenced by an interface must be **public**, otherwise the proxy fails with `IllegalAccessError`.
- `@Required` and `@Validation(...)` on the methods plus `obj.validate(Type.class)` or `obj.asA(Type.class)` replace hand-written "is required" checks. `isA` checks without throwing.
- Validation only sees **`default` methods**. An abstract property is invisible to `validate`/`isA`/`asA`, so input that lacks it passes validation and then fails on access. A `default` method with a **primitive** return type is implicitly REQUIRED even when it reads with a fallback like `booleanValue(false)`. Return a boxed type, or add `@Validation(required = NO)`, when the property is optional.
- The same accessors work for one-off values without an interface: `o.get("importStrategy").to(ImportStrategy.class)` (lenient enum, missing → `null`, unknown → `JsonAccessException` listing the valid values) and `o.get("occurredAt").to(LocalDate.class)`. Don't hand-normalise with `toUpperCase().replace('-', '_')`.
- Raw passthrough of a sub-document (for example GeoJSON): `o.get("geometry").toJson()`.

## Red flags: stop and use the library op

| You are about to… | Do instead |
|---|---|
| write `text(JsonValue)` / `jsonText` / `asString` with a `switch (value.type())` | `getString(k).string()` |
| call `node().getDeclaration()` / `node().textValue()` / `node().booleanValue()` in reader code | `toJson()` / `string()` / `bool()` on the virtual value |
| add `if (v.exists() && !v.isNull() && v.isArray())` before a loop | loop over `getArray(k).values(Index.SKIP)` |
| write `elements(v)` / `object(v)` / `textList(v)` / `textMap(v)` helpers | `values(..)`, `isObject()` once, `stringValues()`, `getMap(k, JsonString.class).toMap(JsonString::string)` |
| guard a lenient op with `isString()` / `isBoolean()` | branch only on the case the op can't take (usually `isObject()`) |
| write a JSON tokenizer for "streaming" | `values(Index.SKIP)` on the lazy tree |
| reject a number where a string is expected without being asked | let `string()` accept it, as Jackson did |

| Rationalization | Reality |
|---|---|
| "The coercion is version-specific, I won't rely on it" | It has been the contract since 1.9 and is pinned by json-tree's tests. Relying on it is what the maintainers expect. Add a probe test if you want a guard. |
| "An explicit check gives a clearer error message" | The exception already names the node type, path and value. Map it once at the boundary. |
| "I'll be defensive, it can't hurt" | It hurts: a strict guard in front of a lenient op caused the 2.43 regression it was meant to prevent. |
| "My helper also handles X" | Then the helper covers X only and delegates the rest (step 5). |

## Common mistakes

- `size()` / `isEmpty()` / `intValue()` / `booleanValue()` on a missing value throw `JsonPathException`. `values()`, `stringValues()`, `string()`, `bool()`, `integer()` and `toMap()` don't.
- `JsonObject.has(k)` and `getMap(k,…)` throw when the value is a primitive or JSON `null`. `getObject(k).getString(..)` doesn't (step 4).
- Object members are duplicate-tolerant. With a caching `Index`, re-occurring keys show the first value.
- `getNumber(k).number()` may return `Integer`, `Long`, `BigInteger` (1.14+) or another `Number`. Use `intValue()`/`longValue()`/`bigDecimal()`, never a cast.
