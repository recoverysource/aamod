---
title: Meetings List Options
layout: single
---

In a "production" deployment of this website, only one meeting list should be used.

---

**[Meeting Map](https://recoverysource.io/aamodule/usage.html#meeting-map)**:

```jinja
Usage: {{</* meeting-map zoom=8 latitude=36.9 longitude=-114.8 */>}}
```

{{< meeting-map zoom=8 latitude=36.9 longitude=-114.8 >}}

---

**[Interactive List](https://recoverysource.io/aamodule/usage.html#meeting-list)**:

```jinja
Usage: {{%/* meeting-list mode="interactive" */%}}
```

{{% meeting-list mode="interactive" %}}

---

**[Meeting Times](https://recoverysource.io/aamodule/usage.html#meeting-list)**:

```jinja
Usage: {{%/* meeting-list mode="time" */%}}
```

{{% meeting-list mode="time" %}}

---

**[Meeting Locations](https://recoverysource.io/aamodule/usage.html#meeting-list)**:

```jinja
Usage: {{%/* meeting-list mode="address" */%}}
```

{{% meeting-list mode="address" %}}

---
