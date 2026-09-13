// Unstructured product reviews → MongoDB (mongosh)
// Student: Sukhada Dhingra  |  PRN: 24070126505  |  Batch: A3
// Course: Big Data Analytics  |  Ubuntu + MongoDB 8.0

const DB_NAME = "sit_bda";
const COLL = "product_reviews";

function banner(title) {
  print("\n==== " + title + " ====");
}

function compactTable(rows, headers) {
  const widths = headers.map((h, i) =>
    Math.max(h.length, ...rows.map((r) => String(r[i] ?? "").length))
  );
  const fmt = (cells) =>
    cells.map((c, i) => String(c).padEnd(widths[i])).join("  ");
  print(fmt(headers));
  print(widths.map((w) => "-".repeat(w)).join("  "));
  rows.forEach((r) => print(fmt(r)));
}

banner("0. server identity");
const hostInfo = db.hostInfo();
printjson({
  host: hostInfo.system.hostname,
  os: hostInfo.os.name + " " + hostInfo.os.version,
  db_version: db.version(),
  student: "Sukhada Dhingra",
  prn: "24070126505",
  batch: "A3",
});

banner("1. database + collection (created before mongoimport)");
db = db.getSiblingDB(DB_NAME);
printjson({
  database: DB_NAME,
  collections: db.getCollectionNames(),
  validator_note: "JSON Schema requires review_id, product, rating, body only — extra fields stay allowed.",
});

banner("2. counts after mongoimport");
print("documents = " + db[COLL].countDocuments());
print("indexes:");
printjson(db[COLL].getIndexes());

banner("3. one sample document (pretty) — nested + optional fields");
printjson(db[COLL].findOne({}, { _id: 0 }));

banner("4. schema-less proof — distinct top-level keys");
const keys = db[COLL]
  .aggregate([
    { $project: { kv: { $objectToArray: "$$ROOT" } } },
    { $unwind: "$kv" },
    { $group: { _id: "$kv.k", n: { $sum: 1 } } },
    { $sort: { n: -1 } },
  ])
  .toArray();
printjson(keys);
print("compact:");
compactTable(
  keys.map((k) => [k._id, k.n, ((100 * k.n) / 300).toFixed(0) + "%"]),
  ["field", "n", "present"]
);

banner("5. CRUD — insertOne with extra nested junk a RDBMS would reject");
const insertRes = db[COLL].insertOne({
  review_id: "REV-LAB-INSERT",
  captured_at: "2026-09-13T20:15:00+05:30",
  channel: "lab-terminal",
  product: {
    sku: "LAB-0001",
    name: "MongoDB lab checklist",
    brand: "SIT-AIML",
    category: "books",
    extra_unstructured: { printed: false, url: "file://queries.js" },
  },
  customer: { handle: "sukhada", city: "Pune", verified_purchase: true, prn: "24070126505" },
  rating: 5,
  title: "Inserted during the Ubuntu lab",
  body: "This document was inserted with mongosh insertOne to demonstrate CRUD on unstructured JSON.",
  tags: ["lab", "nosql", "mongodb", "batch-a3"],
  language: "en",
  viva_note: "No ALTER TABLE was required to add viva_note, tags or nested extra_unstructured.",
});
printjson({ acknowledged: insertRes.acknowledged, insertedId: insertRes.insertedId });
print("count after insert = " + db[COLL].countDocuments());

banner("6. CRUD — find (filter + projection), like SQL WHERE + SELECT cols");
print("electronics, rating >= 4, first 3 (projection hides _id and body):");
printjson(
  db[COLL]
    .find(
      { "product.category": "electronics", rating: { $gte: 4 } },
      { _id: 0, review_id: 1, rating: 1, title: 1, "product.name": 1, "customer.city": 1 }
    )
    .limit(3)
    .toArray()
);

banner("7. CRUD — updateOne");
const upd = db[COLL].updateOne(
  { review_id: "REV-LAB-INSERT" },
  { $set: { lab_verified: true, faculty_flag: "ready-for-viva" }, $inc: { helpful_votes: 1 } }
);
printjson(upd);
printjson(db[COLL].findOne({ review_id: "REV-LAB-INSERT" }, { _id: 0, body: 0 }));

banner("8. CRUD — deleteOne");
const del = db[COLL].deleteOne({ review_id: "REV-LAB-INSERT" });
printjson(del);
print("count after delete = " + db[COLL].countDocuments());

banner("9. count / sort / limit / skip");
print("total = " + db[COLL].countDocuments());
print("rating == 1 count = " + db[COLL].countDocuments({ rating: 1 }));
print("sort by rating desc, skip 5, limit 5:");
printjson(
  db[COLL]
    .find({}, { _id: 0, review_id: 1, rating: 1, "product.name": 1 })
    .sort({ rating: -1, review_id: 1 })
    .skip(5)
    .limit(5)
    .toArray()
);

banner("10. aggregation — reviews and average rating by category");
const byCat = db[COLL]
  .aggregate([
    {
      $group: {
        _id: "$product.category",
        n_reviews: { $sum: 1 },
        avg_rating: { $avg: "$rating" },
        min_rating: { $min: "$rating" },
        max_rating: { $max: "$rating" },
      },
    },
    { $sort: { n_reviews: -1 } },
    {
      $project: {
        _id: 0,
        category: "$_id",
        n_reviews: 1,
        avg_rating: { $round: ["$avg_rating", 2] },
        min_rating: 1,
        max_rating: 1,
      },
    },
  ])
  .toArray();
printjson(byCat);
print("compact:");
compactTable(
  byCat.map((r) => [r.category, r.n_reviews, r.avg_rating, r.min_rating, r.max_rating]),
  ["category", "n", "avg", "min", "max"]
);

banner("11. aggregation — $match Pune + $group by brand");
printjson(
  db[COLL]
    .aggregate([
      { $match: { "customer.city": "Pune" } },
      {
        $group: {
          _id: "$product.brand",
          n: { $sum: 1 },
          avg_rating: { $avg: "$rating" },
        },
      },
      { $sort: { n: -1 } },
      { $limit: 6 },
      {
        $project: {
          _id: 0,
          brand: "$_id",
          n: 1,
          avg_rating: { $round: ["$avg_rating", 2] },
        },
      },
    ])
    .toArray()
);

banner("12. aggregation — unwind tags (array) and rank topics");
printjson(
  db[COLL]
    .aggregate([
      { $match: { tags: { $exists: true, $ne: [] } } },
      { $unwind: "$tags" },
      { $group: { _id: "$tags", n: { $sum: 1 } } },
      { $sort: { n: -1 } },
      { $limit: 8 },
      { $project: { _id: 0, tag: "$_id", n: 1 } },
    ])
    .toArray()
);

banner("13. aggregation — rating histogram + low-star returns");
const facet = db[COLL]
  .aggregate([
    {
      $facet: {
        histogram: [
          { $group: { _id: "$rating", n: { $sum: 1 } } },
          { $sort: { _id: 1 } },
          { $project: { _id: 0, rating: "$_id", n: 1 } },
        ],
        with_return_reason: [
          { $match: { return_reason: { $exists: true } } },
          { $count: "n" },
        ],
        with_seller_reply: [
          { $match: { seller_reply: { $exists: true } } },
          { $count: "n" },
        ],
        with_media: [{ $match: { media: { $exists: true } } }, { $count: "n" }],
      },
    },
  ])
  .toArray()[0];
printjson(facet);
print("compact histogram:");
compactTable(
  facet.histogram.map((r) => [r.rating, r.n]),
  ["rating", "n"]
);
print(
  "optional fields: return_reason=" +
    (facet.with_return_reason[0] || {}).n +
    "  seller_reply=" +
    (facet.with_seller_reply[0] || {}).n +
    "  media=" +
    (facet.with_media[0] || {}).n
);

banner("14. text-ish scan — Ubuntu mentioned in unstructured body");
printjson(
  db[COLL]
    .find(
      { body: /Ubuntu/i },
      { _id: 0, review_id: 1, rating: 1, "product.name": 1, body: 1 }
    )
    .limit(3)
    .toArray()
);

banner("15. done");
print("database = " + DB_NAME + "  collection = " + COLL);
print("Sukhada Dhingra | PRN 24070126505 | Batch A3 | Ubuntu MongoDB lab complete.");
