/*
 * JournalList sql script to process webcrawler.py output.
 *
 * Copyright (c) 2021 Brown Wolf Consulting LLC
 * License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
 *
 * Generate intermediate tables
 *
 */
insert into member_list (srcurl,attr,refurl) select * from trust_txt where attr = "member" order by srcurl, refurl, attr asc;
insert into member_count (srcurl,count) select srcurl, count(*) from member_list group by srcurl;
insert into belongto_list (srcurl,attr,refurl) select * from trust_txt where attr = "belongto" order by srcurl, refurl, attr asc;
insert into belongto_count (srcurl,count) select srcurl, count(*) from belongto_list group by srcurl;
insert into control_list (srcurl,attr,refurl) select * from trust_txt where attr = "control" and srcurl != refurl order by srcurl, refurl, attr asc;
insert into controlledby_list (srcurl,attr,refurl) select * from trust_txt where attr = "controlledby" and srcurl != refurl order by srcurl, refurl, attr asc;
insert into vendor_list (srcurl,attr,refurl) select * from trust_txt where attr = "vendor" order by srcurl, refurl, attr asc;
insert into customer_list (srcurl,attr,refurl) select * from trust_txt where attr = "customer" order by srcurl, refurl, attr asc;
insert into attr_count (srcurl,member_count,belongto_count) select distinct trust_txt.srcurl,(select member_count.count from member_count where member_count.srcurl = trust_txt.srcurl),(select belongto_count.count from belongto_count where belongto_count.srcurl = trust_txt.srcurl) from trust_txt order by srcurl;
update attr_count set member_count = 0 where member_count is null;
update attr_count set belongto_count = 0 where belongto_count is null;
/*
 * Generate the list of symmetric links, where:
 *   member_list.refurl = belongto_list.srcurl and belongto_list.refurl = member_list.srcurl or
 *   control_list.refurl = controlledby_list.srcurl and controlledby_list.refurl = control_list.srcurl or 
 *   vendor_list.refurl = customer_list.srcurl and customer_list.refurl = vendor_list.srcurl
 *
 */
insert into symmetric_list (srcurl1,attr1,refurl1,srcurl2,attr2,refurl2) select * from member_list join belongto_list on member_list.refurl = belongto_list.srcurl and belongto_list.refurl = member_list.srcurl;
insert into symmetric_list (srcurl1,attr1,refurl1,srcurl2,attr2,refurl2) select * from control_list join controlledby_list on control_list.refurl = controlledby_list.srcurl and controlledby_list.refurl = control_list.srcurl;
insert into symmetric_list (srcurl1,attr1,refurl1,srcurl2,attr2,refurl2) select * from vendor_list join customer_list on vendor_list.refurl = customer_list.srcurl and customer_list.refurl = vendor_list.srcurl;
/*
 * Generate the list of asymmetric links, where: the refurl matches the refurl on an HTTP GET error.
 *
 */
insert into asymmetric_list (srcurl,attr,refurl) select trust_txt.srcurl, trust_txt.attr, trust_txt.refurl from trust_txt join http_errors where trust_txt.refurl = http_errors.refurl;
/*
 * Generate the list of associations, publishers, and vendors.
 *
 * Associations = srcurl of any that contain "member" attributes, refurl of any that contain "belongto" attributes, and any refurls they control (Only associations have members, publishers and vendors do not)
 * Publishers = srcurl of any that contain "belongto" attributes and are not associations, any refurls that contain "member" attributes and are not associations, and any refurls they control.
 * Vendors = refurl of any that have "vendor" attribute
 * 
 */
insert into temp_list (srcurl) select distinct srcurl from member_list;
insert into temp_list (srcurl) select distinct refurl from belongto_list;
insert into temp_list (srcurl) select distinct refurl from control_list join temp_list where control_list.srcurl = temp_list.srcurl;
insert into associations_list (srcurl) select distinct srcurl from temp_list order by srcurl;
delete from temp_list where srcurl is not null;
insert into temp_list (srcurl) select distinct srcurl from belongto_list;
insert into temp_list (srcurl) select distinct refurl from member_list;
insert into temp_list (srcurl) select distinct refurl from control_list join temp_list where control_list.srcurl = temp_list.srcurl;
insert into publishers_list (srcurl) select distinct temp_list.srcurl from temp_list where temp_list.srcurl not in (select associations_list.srcurl from associations_list) order by temp_list.srcurl;
insert into vendors_list (srcurl) select distinct refurl from vendor_list;
/*
 * Generate the list of urls that are controlled by the associations, publishers, and vendors
 *
 */
insert into controlled_list (srcurl) select distinct refurl from control_list;
insert into controlled_list (srcurl) select distinct srcurl from controlledby_list;
/*
 * Generate the statistics for associations, publishers, vendors, JournalList members, symmetric and asymmetric relationships.
 *
 */
insert into stats (title) values ("Number of Associations");
update stats set count = (select count (distinct srcurl) from associations_list) where count is null;
insert into stats (title) values ("Number of Publishers");
update stats set count = (select count (distinct srcurl) from publishers_list) where count is null;
insert into stats (title) values ("Number of Vendors");
insert into stats (title,count) values ("Ecosystem Total",0);
update stats set count = (select count (distinct srcurl) from vendors_list) where count is null;
insert into stats (title) values ("Number of Association Members of JournalList");
update stats set count = (select count (distinct associations_list.srcurl) from associations_list join trust_txt where associations_list.srcurl = trust_txt.refurl and trust_txt.srcurl = "https://www.journallist.net/") where count is null;
insert into stats (title) values ("Number of Publisher Members of JournalList");
update stats set count = (select count (distinct publishers_list.srcurl) from publishers_list join trust_txt where publishers_list.srcurl = trust_txt.refurl and trust_txt.srcurl = "https://www.journallist.net/") where count is null;
insert into stats (title) values ("Number of Vendor Members of JournalList");
update stats set count = (select count (distinct vendors_list.srcurl) from vendors_list join trust_txt where vendors_list.srcurl = trust_txt.refurl and trust_txt.srcurl = "https://www.journallist.net/") where count is null;
insert into stats (title,count) values ("JournalList Total",0);
insert into stats (title) values ("Number of trust.txt files Found");
update stats set count = (select count (distinct srcurl) from trust_txt) where count is null;
insert into stats (title) values ("Number of Symmetric Relationships");
update stats set count = (select count (srcurl1) from symmetric_list) where count is null;
insert into stats (title) values ("Number of Asymmetric Relationships");
update stats set count = (select count (srcurl) from asymmetric_list) where count is null;
