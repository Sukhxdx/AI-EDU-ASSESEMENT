// Create the sit_bda.product_reviews collection with a *loose* JSON Schema.
// additionalProperties: true keeps the store schema-less (unstructured / semi-structured).
const DB_NAME = "sit_bda";
const COLL = "product_reviews";

db = db.getSiblingDB(DB_NAME);
db[COLL].drop();
const res = db.createCollection(COLL, {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["review_id", "product", "rating", "body"],
      properties: {
        review_id: { bsonType: "string" },
        rating: { bsonType: ["int", "double", "long"], minimum: 1, maximum: 5 },
        product: { bsonType: "object" },
        body: { bsonType: "string" },
      },
      additionalProperties: true,
    },
  },
});
printjson({
  database: DB_NAME,
  collection: COLL,
  created: res,
  note: "JSON Schema requires four fields only; extra nested keys are allowed.",
});
printjson(db.getCollectionInfos({ name: COLL }));
