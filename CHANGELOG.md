# Version 0.0.9-beta (28 Mar 2023)

### New Features

- Simulating and fitting Pair Distribution Function data using the [PDFFIT](https://github.com/diffpy/diffpy.pdffit2) calculation engine.

### Changes

- GSASII calculation engine has been removed.
- Changed API to define `Job` object as no longer based on the `Sample` class.
- [Xarray objects](https://github.com/pydata/xarray) are now used to store the calculation engine results.
- Overall performance has been improved.

