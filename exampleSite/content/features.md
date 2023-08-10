---
title: Other Features
menu:
  main:
    weight: 30
---

This page demonstrates the use of features that are not used elsewhere on this demo site.

---

**[Report List](https://recoverysource.io/aamod/usage.html#report-list)**:

```jinja
{{</* report-list base="static" path="reports/treasury/" */>}}
```

List of reports which were uploaded to [``<base>/<path>/``](https://github.com/recoverysource/aamod/tree/master/exampleSite/static/reports/treasury/):

{{< report-list base="static" path="reports/treasury/" >}}

---

**[Meeting Info](https://recoverysource.io/aamod/usage.html#meeting-info)**:

```jinja
{{</* meeting-info meeting_id="risingtogether" */>}}
```

Provides a display of information about a meeting.

{{< meeting-info meeting_id="risingtogether" >}}

---
