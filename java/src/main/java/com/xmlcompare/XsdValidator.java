package com.xmlcompare;

import java.io.File;
import javax.xml.XMLConstants;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;

public class XsdValidator {
    public static boolean validate(String xmlPath, String xsdPath) {
        try {
            SchemaFactory factory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
            Schema schema = factory.newSchema(new File(xsdPath));
            Validator validator = schema.newValidator();
            validator.validate(new StreamSource(new File(xmlPath)));
            System.out.println(xmlPath + " is valid against " + xsdPath);
            return true;
        } catch (Exception e) {
            System.out.println("Validation error in " + xmlPath + ": " + e.getMessage());
            return false;
        }
    }

    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: java com.xmlcompare.XsdValidator <xml_file> <xsd_file>");
            System.exit(1);
        }
        boolean valid = validate(args[0], args[1]);
        System.exit(valid ? 0 : 1);
    }
}
