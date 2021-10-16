/*
 * init.sql - JournalList SQLite webcrawl sqlite3 init script
 *
 * Create intermediate tables: list and count by attribute.
 *
 */
CREATE TABLE member_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE member_count ("srcurl" TEXT, "count" INTEGER);
CREATE TABLE belongto_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE belongto_count ("srcurl" TEXT, "count" INTEGER);
CREATE TABLE control_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE control_count ("srcurl" TEXT, "count" INTEGER);
CREATE TABLE controlledby_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE controlledby_count ("srcurl" TEXT, "count" INTEGER);
CREATE TABLE vendor_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE customer_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE attr_count ("srcurl" TEXT, "member_count" INTEGER, "belongto_count" INTEGER);
/*
 * Create output tables: symmetric links, list of associations, publishers, and vendors.
 *
 */
CREATE TABLE symmetric_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE associations_list ("srcurl" TEXT);
CREATE TABLE publishers_list ("srcurl" TEXT);
CREATE TABLE vendors_list ("srcurl" TEXT);
/*
 * Set mode and turn headers on.
 *
 */
.mode csv
.headers on
