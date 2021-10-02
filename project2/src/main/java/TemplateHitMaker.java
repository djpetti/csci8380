import org.apache.commons.text.StringSubstitutor;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

/**
 * Creates HITs based on standard templates.
 */
public class TemplateHitMaker {

    /// The contents of the XML template.
    private final String xmlTemplate;
    /// The contents of the HTML template.
    private final String htmlTemplate;
    /// The HitCreator to use.
    private final HitCreator creator;

    /**
     * @param xmlTemplate The path to the XML template to use for the HIT.
     * @param htmlTemplate The path to the template to use for the HTML embedded in the HIT.
     * @param creator The HitCreator to use for actually making HITs.
     * @throws IOException if reading the templates failed.
     */
    public TemplateHitMaker(final String xmlTemplate, final String htmlTemplate, final HitCreator creator) throws IOException {
        this.creator = creator;

        // Read the templates.
        this.xmlTemplate = new String(Files.readAllBytes(Paths.get(xmlTemplate)));
        this.htmlTemplate = new String(Files.readAllBytes(Paths.get(htmlTemplate)));
    }

    /**
     * Creates a new HIT.
     * @param templateValues The values to use to fill in the HTML template.
     * @return Information about the HIT it created.
     */
    public HitCreator.HITInfo createHit(final Map<String, String> templateValues) {
        StringSubstitutor htmlSubber = new StringSubstitutor(templateValues);
        final String html = htmlSubber.replace(this.htmlTemplate);

        // Substitute this into the XML template.
        Map<String, String> xmlTemplateValues = new HashMap<>();
        xmlTemplateValues.put("question_html", html);
        StringSubstitutor xmlSubber = new StringSubstitutor(xmlTemplateValues);
        final String xml = xmlSubber.replace(this.xmlTemplate);

        // Create the actual HIT.
        return this.creator.createHIT(xml);
    }
}
