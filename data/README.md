# Data

No data are included in this repository, and nothing in `data/` except this
file is tracked by git. To run the notebooks, put calibrated OIFITS files here:

```
data/
├── gravity/                 VLTI/GRAVITY K-band files (*.fits)
├── matisse/
│   └── lband/               VLTI/MATISSE L-band files (*.fits)
├── pionier/                 one combined VLTI/PIONIER file (*.fits)
└── gravity_good_files.txt   optional: GRAVITY file names to fit one by one
                             (one per line); if missing, every file is used
```

GRAVITY files need a `TELLURICS` extension; notebook 01 adds it with
`pmoired.tellcorr` if it is missing.

Public VLTI data can be retrieved from the [ESO Science Archive](https://archive.eso.org/)
and, for PIONIER, the [JMMC OiDB](https://oidb.jmmc.fr/).
