/*
 * Generate intermediate tables
 *
 */
insert into member_list (srcurl,attr,refurl) select * from trust_txt where attr = "member" order by srcurl, refurl asc;
insert into member_count (srcurl,count) select srcurl, count(*) from member_list group by srcurl;
insert into belongto_list (srcurl,attr,refurl) select * from trust_txt where attr = "belongto" order by srcurl, refurl asc;
insert into belongto_count (srcurl,count) select srcurl, count(*) from belongto_list group by srcurl;
insert into control_list (srcurl,attr,refurl) select * from trust_txt where attr = "control" order by srcurl, refurl asc;
insert into controlledby_list (srcurl,attr,refurl) select * from trust_txt where attr = "controlledby" order by srcurl, refurl asc;
insert into vendor_list (srcurl,attr,refurl) select * from trust_txt where attr = "vendor" order by srcurl, refurl asc;
insert into customer_list (srcurl,attr,refurl) select * from trust_txt where attr = "customer" order by srcurl, refurl asc;
insert into attr_count (srcurl,member_count,belongto_count) select distinct trust_txt.srcurl,(select member_count.count from member_count where member_count.srcurl = trust_txt.srcurl),(select belongto_count.count from belongto_count where belongto_count.srcurl = trust_txt.srcurl) from trust_txt;
update attr_count set member_count = 0 where member_count is null;
update attr_count set belongto_count = 0 where belongto_count is null;
/*
 * Generate the list of semmetric links, where:
 *   member_list.refurl = belongto_list.srcurl and belongto_list.refurl = member_list.srcurl or
 *   control_list.refurl = controlledby_list.srcurl and controlledby_list.refurl = control_list.srcurl or 
 *   vendor_list.refurl = customer_list.srcurl and customer_list.refurl = vendor_list.srcurl
 *
 */
insert into symmetric_list (srcurl,attr,refurl) select member_list.srcurl, member_list.attr, belongto_list.srcurl from member_list join belongto_list on member_list.refurl = belongto_list.srcurl and belongto_list.refurl = member_list.srcurl;
insert into symmetric_list (srcurl,attr,refurl) select control_list.srcurl, control_list.attr, controlledby_list.srcurl from control_list join controlledby_list on control_list.refurl = controlledby_list.srcurl and controlledby_list.refurl = control_list.srcurl;
insert into symmetric_list (srcurl,attr,refurl) select vendor_list.srcurl, vendor_list.attr, customer_list.srcurl from vendor_list join customer_list on vendor_list.refurl = customer_list.srcurl and customer_list.refurl = vendor_list.srcurl;
/*
 * Generate the list of associations, publishers, and vendors.
 *
 * Associations = srcurl of those that contain "member" attributes and refurl for any of those that have a matching "control" attribute.
 * Publishers = srcurl of those that contain "belongto" attributes, have more "belongto" attributes than "member" attributes, and refurl for any of those that have a matching "control" attribute.
 * Vendors = refurl of any that have "vendor" attribute.
 * 
 */
insert into associations_list (srcurl) select srcurl from member_count;
insert into associations_list (srcurl) select control_list.refurl from control_list join member_count where control_list.srcurl = member_count.srcurl;
insert into publishers_list (srcurl) select srcurl from attr_count where belongto_count > member_count;
insert into publishers_list (srcurl) select control_list.refurl from control_list join belongto_count where control_list.srcurl = belongto_count.srcurl;
insert into vendors_list (srcurl) select distinct refurl from vendor_list;
