import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class SafeFileReader {

    public static void main(String[] args) {
        String filePath = "data1.txt";
        readFileSafely(filePath);
    }

    public static void readFileSafely(String filePath) {
        BufferedReader reader = null;

        try {
            reader = new BufferedReader(new FileReader(filePath));
            String line;

            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }
            System.out.println("The file has been read successfully.");

        } catch (IOException e) {
            // Fail safely: don't crash, don't show internal details to the user
            System.out.println("Sorry, the file could not be read. Please check the file and try again.");

        } finally {
            // Always try to close the file, even if an error happened
            try {
                if (reader != null) {
                    reader.close();
                }
            } catch (IOException e) {
                System.out.println("There was a problem closing the file.");
            }
        }

    }
}