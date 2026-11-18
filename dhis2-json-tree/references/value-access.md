# json-tree value access: verified reference

Everything here was run against `org.hisp.dhis:json-tree` **1.12.0** (pinned by dhis2-core master, November 2026) and **1.14.0**, with identical results unless marked. Re-run the probe in [Re-verifying](#re-verifying) when you depend on a version outside 1.9–1.14.

Source of truth in the json-tree repo (github.com/dhis2/json-tree): `JsonString`, `JsonBoolean`, `JsonNumber`, `JsonArray`, `JsonAbstractObject`, `JsonTree` (the per-node-type `LazyJson*` classes decide what each terminal op accepts), and `JsonAccess` (accessors for abstract user-type methods).

## The model in four sentences

1. `JsonMixed.of(json)` / `JsonValue.of(json)` / `JsonNode.of(...).lift(JsonAccess.GLOBAL)` give a **virtual** view. Nothing is parsed until a terminal operation needs it.
2. Navigation (`get`, `getString`, `getObject`, `getArray`, `getList`, `getMap`, `as(Type.class)`) only builds a path. It never throws and never checks types.
3. Terminal operations (`string()`, `bool()`, `integer()`, `values()`, `size()`, `toJson()` …) resolve the path against the actual node, convert where there is a reasonable reading, and throw otherwise.
4. The `JsonNode` API (`value.node()`) is the actual tree: strict, throws on missing paths. Reader code rarely needs it, except `root.node().endIndex()` for an up-front syntax check.

## Terminal ops by actual node type

| Terminal op | STRING | NUMBER | BOOLEAN | NULL | missing | ARRAY / OBJECT |
|---|---|---|---|---|---|---|
| `string()` | text (unescaped) | source text (`5.50`, `1e3`, `12345678901234567890`) | `"true"`/`"false"` | `null` | `null` | `JsonTreeException` |
| `string(dflt)` | text | source text | text | `dflt` | `dflt` | `JsonTreeException` |
| `text()` | `Text` view, no copy | source text | text | `null` | `null` | `JsonTreeException` |
| `bool()` | `true`/`false` ignoring case; else `IllegalArgumentException("Not a boolean: …")` (also for `""`) | `JsonTreeException` (also `1`, `0`) | value | `null` | `null` | `JsonTreeException` |
| `booleanValue(dflt)` | as `bool()` | `JsonTreeException` | value | `dflt` | `dflt` | `JsonTreeException` |
| `booleanValue()` | as `bool()` | `JsonTreeException` | value | `JsonTreeException` | `JsonPathException` | `JsonTreeException` |
| `integer()` / `number()` | parsed; `NumberFormatException` if not numeric | value (`integer()` casts 5.5 → 5) | `JsonTreeException` | `null` | `null` | `JsonTreeException` |
| `intValue()` / `longValue()` / `doubleValue()` | parsed | value | `JsonTreeException` | `JsonTreeException` | `JsonPathException` | `JsonTreeException` |
| `intValue(dflt)` | parsed | value | `JsonTreeException` | `dflt` | `dflt` | `JsonTreeException` |
| `bigDecimal()` / `bigInteger()` (1.14+) | parsed | exact | `JsonTreeException` | `null` | `null` | `JsonTreeException` |
| `parsed(fn)` | `fn(string())` | `fn(text)` | `fn(text)` | `null` | `null` | `JsonTreeException` |
| `to(String.class)` | text | source text | text | `null` | `null` | – |
| `toJson()` | `"\"x\""` | source text | source text | `"null"` | `JsonPathException` | raw source (original formatting) |
| `type()` | `STRING` | `NUMBER` | `BOOLEAN` | `NULL` | `null` | `ARRAY`/`OBJECT` |
| `isString()` / `isNumber()` / `isBoolean()` / `isObject()` / `isArray()` | strict actual type; `false` when missing | | | | | |

`number()` returns `Integer` when the value fits, then `Long`, then (1.14+) `BigInteger`. Read through `Number` methods, don't cast.

## Containers

| Op | array | object | NULL | missing | primitive |
|---|---|---|---|---|---|
| `values()` (= `values(Index.SKIP)`; no-arg form not in 1.9.0) | elements as `JsonMixed` | `JsonTreeException` | empty | empty | `JsonTreeException` |
| `values(Index)` | elements | `JsonTreeException` | empty | empty | `JsonTreeException` |
| `for (e : array)`, `stream()` | elements, `Index.AUTO` | – | empty | empty | `JsonTreeException` |
| `stringValues()` | each element's text (`null` element → `"null"`) | – | `[]` | `[]` | `JsonTreeException` |
| `getList(k, T.class).toList(fn)` | mapped, `AUTO` | – | `[]` | `[]` | `JsonTreeException` |
| `entries()` / `keys()` / `names()` | – | members in order | empty | empty | `JsonTreeException` |
| `getMap(k, JsonString.class).toMap(JsonString::string)` | – | map (values via `string()`, so numbers become text) | `{}` | `{}` | `JsonTreeException` |
| `size()` / `isEmpty()` | count | count | `JsonTreeException` | `JsonPathException` | `JsonTreeException` |
| `has(k)` | – | member present (null counts) | `JsonTreeException` | `false` | `JsonTreeException` |
| `getObject(k).getString(x).string()` | `null` | value | `null` | `null` | **`null` (silent)** |

Navigating into a primitive is silent: a `JsonMixed` element `1` viewed through `getString("dataElement")` reads `null`. Check `isObject()` once per entry when a non-object entry must be rejected.

## Existence

| | missing | `null` | value |
|---|---|---|---|
| `exists()` | false | true | true |
| `isNull()` | false | true | false |
| `isUndefined()` | true | true | false |
| `JsonObject.exists(k)` | false | true | true |
| `JsonObject.isUndefined(k)` | true | true | false |

## Exceptions

| Exception | extends | thrown when |
|---|---|---|
| `JsonTreeException` | `UnsupportedOperationException` | the actual node type can't serve the op; message has node type, path and value |
| `JsonPathException` | `NoSuchElementException` | an op that needs existence hits a missing path |
| `JsonAccessException` | `IllegalStateException` | an accessor (`to(..)`, abstract method) can't map, e.g. missing member into a primitive, unknown enum constant |
| `JsonFormatException` | `IllegalArgumentException` | malformed JSON reached while resolving, or `endIndex()` |
| `JsonSchemaException` | `IllegalArgumentException` | `validate` / `asA` failed |
| `IllegalArgumentException` | – | `bool()` on a non-boolean string |
| `NumberFormatException` | `IllegalArgumentException` | numeric op on a non-numeric string |

A reader boundary that catches `JsonTreeException | JsonPathException | JsonAccessException | IllegalArgumentException` covers all of them.

## User-type accessors (abstract methods)

Name mapping: method `value()` → member `value`, `getUsername()` → `username`, `isEnabled()` → `enabled`.

| Return type | Mapping (via) | missing |
|---|---|---|
| `String` | `string()` (numbers and booleans as text) | `null` |
| `Boolean` / `boolean` | `bool()` / `booleanValue()` | `null` / **`JsonAccessException`** |
| `Integer` / `int`, `Long` / `long`, `Double` / `double` | `integer()` / `intValue()` … | `null` / **`JsonAccessException`** |
| `BigDecimal`, `BigInteger` | exact | `null` |
| enum | exact name, then upper-cased with `-`→`_` (`"create-and-update"` → `CREATE_AND_UPDATE`); unknown → `JsonAccessException` listing valid values | `null` |
| `LocalDate`, `LocalDateTime`, `LocalTime` | ISO 8601 string | `null` |
| `UUID`, `URL` | parsed string | `null` |
| `Optional<T>` | wrapped | `Optional.empty()` |
| `List<T>`, `Set<T>`, `Map<K,V>`, `Stream<T>`, records | element-wise | empty |
| `JsonValue` subtypes, `JsonList<T>`, `JsonMap<T>` | view | undefined view |

Types the interface references (enums, nested interfaces) must be `public`. Otherwise `IllegalAccessError` is thrown from the proxy.

## Version history that matters

| Version | Change relevant to readers |
|---|---|
| ≤ 1.8.x (DHIS2 2.43.0–2.43.2.1 shipped 1.8.1) | **Strict**: `string()` on a number or boolean, and `bool()` on `"true"`, throw `JsonTreeException` (`Path $.n does not contain an STRING but a(n) NUMBER`). |
| 1.9 | Lenient terminal ops (`string()` on any scalar; `bool()`/numbers parse strings), `Text`, `to(Class)`, `nodeIfExists()`, accessor registry. Verified: 1.9.0 lenient, 1.8.1 strict. `JsonArray.values()` without an `Index` argument is not in 1.9.0 (use `values(Index.SKIP)`). |
| 1.10 | `entries(Index)`, `asArray()`, `JsonContainer.get(JsonPath)` |
| 1.12 | version pinned by dhis2-core master (November 2026) |
| 1.14 | `bigDecimal()`, `bigInteger()`, `textValues()`; `number()` may return `BigInteger` |

If a codebase is on ≤ 1.8, upgrade json-tree rather than writing coercion helpers.

## Re-verifying

```java
// javac -cp json-tree-X.jar Probe.java && java -cp json-tree-X.jar:. Probe
import org.hisp.dhis.jsontree.*;
public class Probe {
  public static void main(String[] a) {
    JsonObject o = JsonMixed.of("{\"n\":5.50,\"b\":true,\"bt\":\"TRUE\",\"b1\":1,\"arr\":[1]}");
    System.out.println(o.getString("n").string());       // 5.50
    System.out.println(o.getString("b").string());       // true
    System.out.println(o.getBoolean("bt").bool());       // true
    System.out.println(o.getArray("missing").values().count()); // 0
    try { o.getBoolean("b1").bool(); } catch (JsonTreeException e) { System.out.println("1 is not a boolean"); }
    try { o.getString("arr").string(); } catch (JsonTreeException e) { System.out.println(e.getMessage()); }
  }
}
```
