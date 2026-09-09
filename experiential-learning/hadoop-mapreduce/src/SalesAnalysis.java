import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

/**
 * Experiential Learning — Big Data Analytics
 * Hadoop MapReduce: total units sold per product category
 *
 * Input CSV : category,product,units,city
 * Mapper    : emits (category, units)
 * Reducer   : sums units for each category
 *
 * Student : Sukhada Dhingra
 */
public class SalesAnalysis {

    public static class CategoryMapper
            extends Mapper<LongWritable, Text, Text, IntWritable> {

        private final Text category = new Text();
        private final IntWritable units = new IntWritable();

        @Override
        public void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString().trim();
            if (line.isEmpty() || line.toLowerCase().startsWith("category")) {
                return;
            }
            String[] parts = line.split(",");
            if (parts.length < 3) {
                return;
            }
            try {
                category.set(parts[0].trim().toLowerCase());
                units.set(Integer.parseInt(parts[2].trim()));
                context.write(category, units);
            } catch (NumberFormatException ignored) {
                // skip malformed rows
            }
        }
    }

    public static class SumReducer
            extends Reducer<Text, IntWritable, Text, IntWritable> {

        private final IntWritable total = new IntWritable();

        @Override
        public void reduce(Text key, Iterable<IntWritable> values, Context context)
                throws IOException, InterruptedException {
            int sum = 0;
            for (IntWritable value : values) {
                sum += value.get();
            }
            total.set(sum);
            context.write(key, total);
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println("Usage: SalesAnalysis <input path> <output path>");
            System.exit(2);
        }

        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "sales by category");
        job.setJarByClass(SalesAnalysis.class);
        job.setMapperClass(CategoryMapper.class);
        job.setCombinerClass(SumReducer.class);
        job.setReducerClass(SumReducer.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
