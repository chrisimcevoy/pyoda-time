# Changelog

## [0.8.0](https://github.com/chrisimcevoy/pyoda-time/compare/v0.7.1...v0.8.0) (2024-05-28)


### Features

* `LocalTime` pseudomutator tests ([#128](https://github.com/chrisimcevoy/pyoda-time/issues/128)) ([7419cf8](https://github.com/chrisimcevoy/pyoda-time/commit/7419cf8a49daae7484cd7c0d043577595acc14bf))
* baseline `TzdbDateTimeZoneSource` functionality ([#146](https://github.com/chrisimcevoy/pyoda-time/issues/146)) ([7e05fd3](https://github.com/chrisimcevoy/pyoda-time/commit/7e05fd3e2db29c1471ebff198760d78c6cb3e3f6))
* implement `__hash__`, `__repr__` and `__format__` for `LocalTime` ([#129](https://github.com/chrisimcevoy/pyoda-time/issues/129)) ([4a5a403](https://github.com/chrisimcevoy/pyoda-time/commit/4a5a403ddc0fad26beed8701b286e657604fdd40))
* implement `LocalTime` conversions ([#121](https://github.com/chrisimcevoy/pyoda-time/issues/121)) ([79a2152](https://github.com/chrisimcevoy/pyoda-time/commit/79a2152cd4d135a95df857301c95ad7e4e1c55f7))
* implement `LocalTime` operators ([#127](https://github.com/chrisimcevoy/pyoda-time/issues/127)) ([f23df54](https://github.com/chrisimcevoy/pyoda-time/commit/f23df54dc9da8e88940e63c20924e94eb4fc7f79))
* port `AmbiguousTimeException` ([#136](https://github.com/chrisimcevoy/pyoda-time/issues/136)) ([fbd4c6f](https://github.com/chrisimcevoy/pyoda-time/commit/fbd4c6f260bfb5f97dd9ec6f67269abb788edcc9))
* port `AnnualDate` ([#151](https://github.com/chrisimcevoy/pyoda-time/issues/151)) ([8b8751e](https://github.com/chrisimcevoy/pyoda-time/commit/8b8751eb7783ecf1db09ed02e372c7ba8cc55960))
* port `DateAdjusters` ([#150](https://github.com/chrisimcevoy/pyoda-time/issues/150)) ([4931381](https://github.com/chrisimcevoy/pyoda-time/commit/4931381ed0fd60af3c2741338b13b9cfba842099))
* port `FormatHelper` ([#119](https://github.com/chrisimcevoy/pyoda-time/issues/119)) ([3ffdccd](https://github.com/chrisimcevoy/pyoda-time/commit/3ffdccd7d93e75d899e88fb8ecc0398376688166))
* port `IDateTimeZoneSource` ([#140](https://github.com/chrisimcevoy/pyoda-time/issues/140)) ([f8e7b93](https://github.com/chrisimcevoy/pyoda-time/commit/f8e7b9381aa2a524bed889cfdb8c01798682ae2b))
* port `Interval` ([#142](https://github.com/chrisimcevoy/pyoda-time/issues/142)) ([91572a0](https://github.com/chrisimcevoy/pyoda-time/commit/91572a0ef6a7b35c27f140cdd80f491c14675664))
* port `LocalInstant` ([#132](https://github.com/chrisimcevoy/pyoda-time/issues/132)) ([da186b0](https://github.com/chrisimcevoy/pyoda-time/commit/da186b0d616bcdd3b8b6331048e70eae97c9efcc))
* port `LocalTimePattern` ([#120](https://github.com/chrisimcevoy/pyoda-time/issues/120)) ([5a57268](https://github.com/chrisimcevoy/pyoda-time/commit/5a5726808f2373dc38256deb92e503c9e4f40d35))
* port `OffsetTime` ([#137](https://github.com/chrisimcevoy/pyoda-time/issues/137)) ([1d71816](https://github.com/chrisimcevoy/pyoda-time/commit/1d718166a0ca8b4d666d5b6657cb091d65b84bbd))
* port `PreCalculatedDateTimeZone` ([#144](https://github.com/chrisimcevoy/pyoda-time/issues/144)) ([8e3326c](https://github.com/chrisimcevoy/pyoda-time/commit/8e3326c9805b70fca373a05fc80ca3346847ca2a))
* port `SkippedTimeException` ([#135](https://github.com/chrisimcevoy/pyoda-time/issues/135)) ([ea5b9bd](https://github.com/chrisimcevoy/pyoda-time/commit/ea5b9bdb0770f3c950d0ef0837a07e28bd2619dd))
* port `TimeAdjusters` ([3622f7d](https://github.com/chrisimcevoy/pyoda-time/commit/3622f7d3a16e2749e99f93793697415c59dfd7b6))
* port `Transition` ([#131](https://github.com/chrisimcevoy/pyoda-time/issues/131)) ([da43ae3](https://github.com/chrisimcevoy/pyoda-time/commit/da43ae31c339c055cda5add169409f850dcc34a9))
* port `TransitionMode` enum ([#115](https://github.com/chrisimcevoy/pyoda-time/issues/115)) ([a876393](https://github.com/chrisimcevoy/pyoda-time/commit/a8763933d50beddcb7dadf39f9d8f907de6de01b))
* port `ZoneLocalMapping`, `PrecalculatedDateTimeZone` & `StandardDaylightAlternatingMap` ([#141](https://github.com/chrisimcevoy/pyoda-time/issues/141)) ([7394039](https://github.com/chrisimcevoy/pyoda-time/commit/7394039743b424154dd6cb1cfc8bd77b720cc13c))
* port `ZoneRecurrence` ([#134](https://github.com/chrisimcevoy/pyoda-time/issues/134)) ([7222e10](https://github.com/chrisimcevoy/pyoda-time/commit/7222e106c7e446dbf6ea2a24b1aad58e6b313f05))
* port `ZoneYearOffset` ([#130](https://github.com/chrisimcevoy/pyoda-time/issues/130)) ([5830937](https://github.com/chrisimcevoy/pyoda-time/commit/5830937e3b16dfeb888f831fb39b7c9d72ce1353))
* use `InstantPattern` in `Instant.__repr__` ([#139](https://github.com/chrisimcevoy/pyoda-time/issues/139)) ([a126278](https://github.com/chrisimcevoy/pyoda-time/commit/a1262789c3d2b0f1217123684ceef29455217854))


### Bug Fixes

* `_LocalInstant._is_valid` ([84db8d0](https://github.com/chrisimcevoy/pyoda-time/commit/84db8d07c04fa7178e764ac0f06bce158dde3476))

## [0.7.1](https://github.com/chrisimcevoy/pyoda-time/compare/v0.7.0...v0.7.1) (2024-05-17)


### Documentation

* switch to pre-alpha trove classifier ([#113](https://github.com/chrisimcevoy/pyoda-time/issues/113)) ([384a3d5](https://github.com/chrisimcevoy/pyoda-time/commit/384a3d578838d8182e0f70a35796f06ec6eea819))

## [0.7.0](https://github.com/chrisimcevoy/pyoda-time/compare/v0.6.0...v0.7.0) (2024-05-17)


### Features

* Implement `InstantPattern` ([#83](https://github.com/chrisimcevoy/pyoda-time/issues/83)) ([5508231](https://github.com/chrisimcevoy/pyoda-time/commit/550823120d39434fab6537ab01ca36e047e39d5f))
* implement `LocalDate` and `LocalTime` constructors ([#100](https://github.com/chrisimcevoy/pyoda-time/issues/100)) ([7a4f294](https://github.com/chrisimcevoy/pyoda-time/commit/7a4f294e1a0ac9b0c17d4cccb0d2cd84239f4d90))
* implement `LocalDatePattern` ([#87](https://github.com/chrisimcevoy/pyoda-time/issues/87)) ([c2fb6eb](https://github.com/chrisimcevoy/pyoda-time/commit/c2fb6eb454bfb702238865eae51fe3da55b89daf))
* implement `LocalDateTimePattern` ([#85](https://github.com/chrisimcevoy/pyoda-time/issues/85)) ([ee62700](https://github.com/chrisimcevoy/pyoda-time/commit/ee627009ba51dc7a6484220194fe7bf0578fa685))
* Implement `OffsetPattern` ([#55](https://github.com/chrisimcevoy/pyoda-time/issues/55)) ([c765b70](https://github.com/chrisimcevoy/pyoda-time/commit/c765b70ead76a0620ff80ee7ef0fdab246f81b2d))
* Implement `PyodaFormatInfo` ([#77](https://github.com/chrisimcevoy/pyoda-time/issues/77)) ([12775e5](https://github.com/chrisimcevoy/pyoda-time/commit/12775e55029d2e683d9397605998e0e68bea273f))
* implement duration ([#47](https://github.com/chrisimcevoy/pyoda-time/issues/47)) ([10c1ab0](https://github.com/chrisimcevoy/pyoda-time/commit/10c1ab0c2ee330ccb1f1e2595bbba6f0a99bf757))
* port `time_zones.cldr` and `time_zones.io` namespaces ([#109](https://github.com/chrisimcevoy/pyoda-time/issues/109)) ([626d4e1](https://github.com/chrisimcevoy/pyoda-time/commit/626d4e131195bbb1297c03878ce609d03025ef31))


### Bug Fixes

* enforce consistent comparison operator behaviour ([#95](https://github.com/chrisimcevoy/pyoda-time/issues/95)) ([95cfca1](https://github.com/chrisimcevoy/pyoda-time/commit/95cfca197b7d68a6169b9fdd585fae204501a611))
* move version.py out of package ([#101](https://github.com/chrisimcevoy/pyoda-time/issues/101)) ([6c5bb1b](https://github.com/chrisimcevoy/pyoda-time/commit/6c5bb1be326c85702795949e756587035909ce90))


### Documentation

* add readthedocs config ([#62](https://github.com/chrisimcevoy/pyoda-time/issues/62)) ([dceaab7](https://github.com/chrisimcevoy/pyoda-time/commit/dceaab7a82bf7db6574acfd8ad3e0398423300d3))
* add sphinx project ([#61](https://github.com/chrisimcevoy/pyoda-time/issues/61)) ([c21a87f](https://github.com/chrisimcevoy/pyoda-time/commit/c21a87f695525596a2f90e9c3a985eafbe5579f0))
* fix path to sphinx conf in .readthedocs.yaml ([#63](https://github.com/chrisimcevoy/pyoda-time/issues/63)) ([4396606](https://github.com/chrisimcevoy/pyoda-time/commit/4396606cec2b6fe0d01c1c6ddbfd170d7991bd57))
* set custom domain as canonical url in sphinx ([#65](https://github.com/chrisimcevoy/pyoda-time/issues/65)) ([c2cf6ac](https://github.com/chrisimcevoy/pyoda-time/commit/c2cf6ac3e8f9f04656cafc537dfed03eeb1a6e9f))
* update license badge and trove classifiers ([#42](https://github.com/chrisimcevoy/pyoda-time/issues/42)) ([e22c0b8](https://github.com/chrisimcevoy/pyoda-time/commit/e22c0b846b201ec153f2db653d2d7e0a3fe7c7a9))
* update README.md and add CONTRIBUTING.md ([#56](https://github.com/chrisimcevoy/pyoda-time/issues/56)) ([e946b9c](https://github.com/chrisimcevoy/pyoda-time/commit/e946b9c2964e444fd3c43f35d94f4972f920ea8d))
* update README.md to point to readthedocs ([#67](https://github.com/chrisimcevoy/pyoda-time/issues/67)) ([56b6494](https://github.com/chrisimcevoy/pyoda-time/commit/56b6494444d8e3bb2d81f1e0176008edbfed40fc))

## [0.6.0](https://github.com/chrisimcevoy/pyoda-time/compare/0.5.0...v0.6.0) (2024-01-12)


### Features

* adopt apache 2.0 license ([#38](https://github.com/chrisimcevoy/pyoda-time/issues/38)) ([cb9bc5e](https://github.com/chrisimcevoy/pyoda-time/commit/cb9bc5eec23ebf3a0f91c3ecba5509dc6426e24e))
* **api:** Tidy up public API & enforce via tests ([#16](https://github.com/chrisimcevoy/pyoda-time/issues/16)) ([5e7d8fa](https://github.com/chrisimcevoy/pyoda-time/commit/5e7d8fa8a5578e328e2c10d044cd136c1610a7b6))
* implement islamic, persian and um al qura calendars ([#19](https://github.com/chrisimcevoy/pyoda-time/issues/19)) ([705a0a3](https://github.com/chrisimcevoy/pyoda-time/commit/705a0a39729e413b5e8e1b2b6da899a7eb6aad00))
* implement period ([#36](https://github.com/chrisimcevoy/pyoda-time/issues/36)) ([59ee7b5](https://github.com/chrisimcevoy/pyoda-time/commit/59ee7b5bdff028cdcd33c1e8fcf1ec105c718b59))
* implement week year rules ([#30](https://github.com/chrisimcevoy/pyoda-time/issues/30)) ([0f578a5](https://github.com/chrisimcevoy/pyoda-time/commit/0f578a5c592cfba27893f4d1e9108c9b0dece3dc))
* include py.typed file ([#40](https://github.com/chrisimcevoy/pyoda-time/issues/40)) ([36e09d2](https://github.com/chrisimcevoy/pyoda-time/commit/36e09d21d7a1c82f5516c8345be0a5f0e6696bd0))


### Bug Fixes

* add missing calendar tests ([#20](https://github.com/chrisimcevoy/pyoda-time/issues/20)) ([1ab7938](https://github.com/chrisimcevoy/pyoda-time/commit/1ab7938eaf037947361d0a47a9ab3b29aa7780e0))
* include version.py file ([1ed94f8](https://github.com/chrisimcevoy/pyoda-time/commit/1ed94f80321a87d0e229959ef21711d40d470465))
* **Instant:** Raise OverflowError when Instant._plus() is passed a sufficiently large or small Offset ([#18](https://github.com/chrisimcevoy/pyoda-time/issues/18)) ([c42f124](https://github.com/chrisimcevoy/pyoda-time/commit/c42f1240ee572fc2f7447a16fa5d125968d92c90))
* **pre-commit:** add v prefix to commitizen pre-commit hook rev ([#26](https://github.com/chrisimcevoy/pyoda-time/issues/26)) ([999f7a7](https://github.com/chrisimcevoy/pyoda-time/commit/999f7a78882767cceb06aeeb467d6e2790fbc851))
* remove v3 release-please config ([#29](https://github.com/chrisimcevoy/pyoda-time/issues/29)) ([eda98bb](https://github.com/chrisimcevoy/pyoda-time/commit/eda98bb2e348ea3ae72a3fafd877995259712fe0))

## [0.5.0](https://github.com/chrisimcevoy/pyoda-time/compare/0.4.0...0.5.0) (2023-11-22)


### 🚀 Features

* **api:** add PyodaConstants class ([#15](https://github.com/chrisimcevoy/pyoda-time/issues/15)) ([6f80b20](https://github.com/chrisimcevoy/pyoda-time/commit/6f80b20f848219333c97d6b1e2fc1968e975c94d))


### 🐛 Bug Fixes

* **changelog:** make CHANGELOG.md play nice with release-please-action ([#13](https://github.com/chrisimcevoy/pyoda-time/issues/13)) ([76062f9](https://github.com/chrisimcevoy/pyoda-time/commit/76062f967e4a2a771ae0055ddc72fbaa1664a72e))
* **typing:** add ruff rules & fix type hint ([#10](https://github.com/chrisimcevoy/pyoda-time/issues/10)) ([4a3b702](https://github.com/chrisimcevoy/pyoda-time/commit/4a3b7023cac85a6ff4cd7b9968c658d04119a9ce))

## [0.4.0](https://github.com/chrisimcevoy/pyoda-time/compare/0.3.0...0.4.0) (2023-11-21)

### 🚀 Features

* Implement Hebrew, Coptic and Badi calendars ([#8](https://github.com/chrisimcevoy/pyoda-time/issues/8)) ([fecd4c6](https://github.com/chrisimcevoy/pyoda-time/commit/fecd4c65ecf0cbb7ec1c0bd0cb8909a45c39cbef))
