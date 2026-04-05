import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import java.nio.file.Files;
import java.nio.file.Paths;

class XsdValidatorTest {
    @Test
    void validXmlPasses() throws Exception {
        String xml = "src/test/resources/valid.xml";
        String xsd = "src/test/resources/schema.xsd";
        if (Files.exists(Paths.get(xml)) && Files.exists(Paths.get(xsd))) {
            assertTrue(com.xmlcompare.XsdValidator.validate(xml, xsd));
        }
    }

    @Test
    void invalidXmlFails() throws Exception {
        String xml = "src/test/resources/invalid.xml";
        String xsd = "src/test/resources/schema.xsd";
        if (Files.exists(Paths.get(xml)) && Files.exists(Paths.get(xsd))) {
            assertFalse(com.xmlcompare.XsdValidator.validate(xml, xsd));
        }
    }
}
