# Changelog

## [2.98.1](https://github.com/safe-global/safe-config-service/compare/v2.98.0...v2.98.1) (2026-07-22)


### Bug Fixes

* **ci:** make prod health gate VPN-independent; fix VPN log perms ([3fe7647](https://github.com/safe-global/safe-config-service/commit/3fe764778b1cd026b14fd62c37f9e8b70f2eb2aa))
* **ci:** Make prod health gate VPN-independent; fix VPN log perms ([#1636](https://github.com/safe-global/safe-config-service/issues/1636)) ([3fe7647](https://github.com/safe-global/safe-config-service/commit/3fe764778b1cd026b14fd62c37f9e8b70f2eb2aa))

## [2.98.0](https://github.com/safe-global/safe-config-service/compare/v2.97.0...v2.98.0) (2026-07-22)


### Features

* **ci:** Add workflow_dispatch recovery path to production.yml ([#1622](https://github.com/safe-global/safe-config-service/issues/1622)) ([61c5675](https://github.com/safe-global/safe-config-service/commit/61c56758c034286aa3c385d2e033129ee5a3cd47))


### Bug Fixes

* **ci:** correct safe-apps post-deploy check to array length ([63d60be](https://github.com/safe-global/safe-config-service/commit/63d60bec4e7d81302eeda054b480699e051688b8))
* **ci:** Correct safe-apps post-deploy check to array length ([#1624](https://github.com/safe-global/safe-config-service/issues/1624)) ([63d60be](https://github.com/safe-global/safe-config-service/commit/63d60bec4e7d81302eeda054b480699e051688b8))
* **ci:** use env flags for secrets conditionals in _deploy.yml ([#1621](https://github.com/safe-global/safe-config-service/issues/1621)) ([188d940](https://github.com/safe-global/safe-config-service/commit/188d940001a594a8a47b7cf85fe89cf29c683da2))

## [2.97.0](https://github.com/safe-global/safe-config-service/compare/v2.96.2...v2.97.0) (2026-07-08)


### Features

* Add Datadog APM instrumentation via ddtrace SDK ([#1600](https://github.com/safe-global/safe-config-service/issues/1600)) ([144f425](https://github.com/safe-global/safe-config-service/commit/144f425e3ec21c99daa865c7985f2c39d452ba2f))
* Add pull-request and staging CI/CD workflows ([3e78a94](https://github.com/safe-global/safe-config-service/commit/3e78a94cbb0e439bc1fb84fc5c7965f90ba776ea))
* Add pull-request and staging CI/CD workflows ([#1602](https://github.com/safe-global/safe-config-service/issues/1602)) ([3e78a94](https://github.com/safe-global/safe-config-service/commit/3e78a94cbb0e439bc1fb84fc5c7965f90ba776ea))
* Add reusable workflows locally and wire pull-request + staging CI/CD ([3e78a94](https://github.com/safe-global/safe-config-service/commit/3e78a94cbb0e439bc1fb84fc5c7965f90ba776ea))
* Adding workflow_dispatch to staging.yml so the soak can run without empty commits ([#1615](https://github.com/safe-global/safe-config-service/issues/1615)) ([b5a6be6](https://github.com/safe-global/safe-config-service/commit/b5a6be608da916e7acdfc3ec35331e5a85662427))
* **ci:** deploy imageTag bump via PR instead of direct push ([#1616](https://github.com/safe-global/safe-config-service/issues/1616)) ([b24d036](https://github.com/safe-global/safe-config-service/commit/b24d036942ae4fe6fbf3b1748d8edf78cf1e07d5))


### Bug Fixes

* **_deploy:** Switch to --squash merge for Verified badge on infra commits ([#1617](https://github.com/safe-global/safe-config-service/issues/1617)) ([2dea15a](https://github.com/safe-global/safe-config-service/commit/2dea15acc73e44761d14f6b49c6e3d2b2441e13d))
* **ci:** move vpn/aws/argocd inputs to secrets, fix staging id-token perm ([0eadf84](https://github.com/safe-global/safe-config-service/commit/0eadf841f06c08f53ec9c2fb2630f23722d3eeeb))
* **ci:** Move vpn/aws/argocd inputs to secrets, fix staging id-token perm ([#1620](https://github.com/safe-global/safe-config-service/issues/1620)) ([0eadf84](https://github.com/safe-global/safe-config-service/commit/0eadf841f06c08f53ec9c2fb2630f23722d3eeeb))
