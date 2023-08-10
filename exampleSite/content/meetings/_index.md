---
title: Meetings List Options
layout: single
---

In a "production" deployment of this website, only one meeting list should be used.

---

**[Meeting Map](https://recoverysource.io/aamod/usage.html#meeting-map)**:

```jinja
{{</* meeting-map zoom=8 latitude=36.9 longitude=-114.8 */>}}
```

{{< meeting-map zoom=8 latitude=36.9 longitude=-114.8 >}}

---

**[Interactive List](https://recoverysource.io/aamod/usage.html#meeting-list)**:

```jinja
{{%/* meeting-list mode="interactive" */%}}
```

{{% meeting-list mode="interactive" %}}

---

**[Meeting Times](https://recoverysource.io/aamod/usage.html#meeting-list)**:

```jinja
{{%/* meeting-list mode="time" */%}}
```

{{% meeting-list mode="time" %}}

---

**[Meeting Locations](https://recoverysource.io/aamod/usage.html#meeting-list)**:

```jinja
{{%/* meeting-list mode="address" */%}}
```

{{% meeting-list mode="address" %}}

---
