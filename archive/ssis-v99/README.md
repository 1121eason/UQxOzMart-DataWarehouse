# Historical SSIS build 99

The supplied `bin/Development/Assignment1.ispac` embeds a `Package.dtsx` with `VersionBuild=99`. The loose project package is build 101. This archive preserves the earlier artifact separately so it cannot be mistaken for the current pipeline.

The public ISPAC has been repackaged to remove encrypted password elements and password verifiers, apply `DontSaveSensitive`, and use the same portable connection defaults as the canonical source. It is not byte-identical to the original ISPAC and has not been rebuilt or deployed with Visual Studio.

Open [the canonical project](../../ssis/Assignment1/Assignment1.dtproj), configure your environment and build a fresh artifact for execution. The [input inventory](../../docs/evidence/input-inventory.json) retains the original ISPAC hash.
