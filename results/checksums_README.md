# Integrity verification

`checksums_sha256.txt` lists SHA-256 hashes for every file in this deposit, one line per file in the form
hash + two spaces + relative path (forward slashes, LF line endings), so the standard command works from the package root:

    sha256sum -c 08_qc/checksums_sha256.txt

Notes
- The two verification files (`checksums_sha256.txt` and `file_inventory_and_checksums.csv`) are self-referential: their hashes
  were computed before they were finalised, so they are excluded from the check and are marked as self-references in the inventory.
- This file contains hash lines only, so `sha256sum -c` produces no formatting warnings.
- The `rows` column of `file_inventory_and_checksums.csv` counts data rows, excluding the header.
