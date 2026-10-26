# Canonical SSIS source

Open `Assignment1.dtproj` in a compatible Visual Studio SSIS environment. `Package.dtsx` is the supplied loose package, build 101, with public connection defaults and sensitive values removed. The project targets `SQLServer2025`.

Four dimension tasks are saved disabled and the fact task enabled. Read [setup](../../docs/setup.md) before running a fresh load. This repository preserves that saved state rather than implying the source was freshly executed.

`Assignment1.database` is project XML metadata. `Project.params` is the supplied empty parameter document. The original `.dtproj.user`, local build outputs and caches are excluded. The earlier sanitised ISPAC is under [archive](../../archive/ssis-v99/README.md).
