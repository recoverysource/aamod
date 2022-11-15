aamod
=====

AA Mod (``aamod``) is a website solution for Alcoholics Anonymous (A.A.)-related
website, with a focus on sharing meeting information in a fast and secure manner.

AA Mod is a Subtheme for [Hugo](https://gohugo.io/) with some extra documentation,
scripts, etc. Hugo is a website framework that builds statically-generated websites.
These static websites are immune to the vast majority of new vulnerabilities,
meaning your website will only ever have to change/update for content or design.

This added documentation walks a user through deploying this website and hosting
it using [Github Pages](https://pages.github.com/). If you have decided you want
what [we](https://area63aa.org/) and want to avoid major hurdles to get there,
then you are ready to take [certain steps](https://recoverysource.github.io/aamod/website.html).

Website Template
----------------

Although it is possible to start a brand new Hugo website from scratch, import
this theme, and get everything configured correctly, this
[website (Hugo) template](https://github.com/recoverysource/hugo-website) let's you
skip that and get right from deployment to long-term maintenance (content updates).

This theme is mostly a copy of the ``exampleSite/`` within this repository, along
with Makefile/Github Actions/etc., which are used to automatically build the
website when any changes are made.

If all of this sounds complex, then the [Hugo website template](https://github.com/recoverysource/hugo-website)
is exactly what you need and the [New Website instructions](https://recoverysource.github.io/aamod/website.html#new-website)
were written for you.

Subtheme
--------

AA Mod is a subtheme of [Mainroad](https://themes.gohugo.io/themes/mainroad/)

``AAmod`` can be used like any other theme with the exception of requiring the
[Mainroad](https://themes.gohugo.io/themes/mainroad/) subtheme be loaded first.
This parent theme provides some great documentation which is not replicated here.

Additional Steps:

```
git submodule add https://github.com/recoverysource/aamod.git themes/aamod
theme = ["aamod", "mainroad"]
```

Features
--------

The primary feature of ``aamod`` is turning easily maintained meeting data
into content suitable for hugo to turn into a website. This is currently done
using the ``generate_content.py``--although it may be more suitable as a hugo
module.

- Build a json file suitable for use with [Meeting Guide](https://www.aa.org/meeting-guide-app)
- Build pages for each meeting
- Build meeting schedule list (by time and by zip)
- Build meeting schedule pdf (printable)
- Maintains internationalization (i18n) support
- Config-customized sidebar menus
- Report list function embed a list of uploaded files, such as treasury reports
