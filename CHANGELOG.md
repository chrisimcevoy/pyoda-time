# Changelog

## [0.6.0](https://github.com/chrisimcevoy/pyoda-time/compare/0.5.0...0.6.0) (2023-12-13)


### 🚀 Features

* **api:** Tidy up public API & enforce via tests ([#16](https://github.com/chrisimcevoy/pyoda-time/issues/16)) ([5e7d8fa](https://github.com/chrisimcevoy/pyoda-time/commit/5e7d8fa8a5578e328e2c10d044cd136c1610a7b6))
* implement islamic, persian and um al qura calendars ([#19](https://github.com/chrisimcevoy/pyoda-time/issues/19)) ([705a0a3](https://github.com/chrisimcevoy/pyoda-time/commit/705a0a39729e413b5e8e1b2b6da899a7eb6aad00))


### 🐛 Bug Fixes

* **Instant:** Raise OverflowError when Instant._plus() is passed a sufficiently large or small Offset ([#18](https://github.com/chrisimcevoy/pyoda-time/issues/18)) ([c42f124](https://github.com/chrisimcevoy/pyoda-time/commit/c42f1240ee572fc2f7447a16fa5d125968d92c90))
* **pre-commit:** add v prefix to commitizen pre-commit hook rev ([#26](https://github.com/chrisimcevoy/pyoda-time/issues/26)) ([999f7a7](https://github.com/chrisimcevoy/pyoda-time/commit/999f7a78882767cceb06aeeb467d6e2790fbc851))

## [0.5.0](https://github.com/chrisimcevoy/pyoda-time/compare/0.4.0...0.5.0) (2023-11-22)


### 🚀 Features

* **api:** add PyodaConstants class ([#15](https://github.com/chrisimcevoy/pyoda-time/issues/15)) ([6f80b20](https://github.com/chrisimcevoy/pyoda-time/commit/6f80b20f848219333c97d6b1e2fc1968e975c94d))


### 🐛 Bug Fixes

* **changelog:** make CHANGELOG.md play nice with release-please-action ([#13](https://github.com/chrisimcevoy/pyoda-time/issues/13)) ([76062f9](https://github.com/chrisimcevoy/pyoda-time/commit/76062f967e4a2a771ae0055ddc72fbaa1664a72e))
* **typing:** add ruff rules & fix type hint ([#10](https://github.com/chrisimcevoy/pyoda-time/issues/10)) ([4a3b702](https://github.com/chrisimcevoy/pyoda-time/commit/4a3b7023cac85a6ff4cd7b9968c658d04119a9ce))

## [0.4.0](https://github.com/chrisimcevoy/pyoda-time/compare/0.3.0...0.4.0) (2023-11-21)

### 🚀 Features

* Implement Hebrew, Coptic and Badi calendars ([#8](https://github.com/chrisimcevoy/pyoda-time/issues/8)) ([fecd4c6](https://github.com/chrisimcevoy/pyoda-time/commit/fecd4c65ecf0cbb7ec1c0bd0cb8909a45c39cbef))
