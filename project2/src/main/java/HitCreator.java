import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import com.amazonaws.services.mturk.AmazonMTurk;
import com.amazonaws.services.mturk.model.Comparator;
import com.amazonaws.services.mturk.model.CreateHITRequest;
import com.amazonaws.services.mturk.model.CreateHITResult;
import com.amazonaws.services.mturk.model.Locale;
import com.amazonaws.services.mturk.model.QualificationRequirement;

/*
 * Before connecting to MTurk, set up your AWS account and IAM settings as described here:
 * https://blog.mturk.com/how-to-use-iam-to-control-api-access-to-your-mturk-account-76fe2c2e66e2
 *
 * Configure your AWS credentials as described here:
 * http://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/credentials.html
 *
 */

public class HitCreator {

    private final AmazonMTurk client;

    /**
     * @param client The client to use for connecting to Mechanical Turk.
     */
    public HitCreator(final AmazonMTurk client) {
        this.client = client;
    }

    public static final class HITInfo {
        private final String hitId;
        private final String hitTypeId;

        private HITInfo(final String hitId, final String hitTypeId) {
            this.hitId = hitId;
            this.hitTypeId = hitTypeId;
        }

        public String getHITId() {
            return this.hitId;
        }

        public String getHITTypeId() {
            return this.hitTypeId;
        }
    }

    /**
     * Creates a new HIT containing the specified data.
     *
     * @param questionXml The raw XML to use for the HIT.
     * @return Information about the HIT it created.
     */
    public HITInfo createHIT(final String questionXml) {
        // QualificationRequirement: Locale IN (US, CA)
        QualificationRequirement localeRequirement = new QualificationRequirement();
        localeRequirement.setQualificationTypeId("00000000000000000071");
        localeRequirement.setComparator(Comparator.In);
        List<Locale> localeValues = new ArrayList<>();
        localeValues.add(new Locale().withCountry("US"));
        localeValues.add(new Locale().withCountry("CA"));
        localeRequirement.setLocaleValues(localeValues);

        CreateHITRequest request = new CreateHITRequest();
        request.setMaxAssignments(10);
        request.setLifetimeInSeconds(600L);
        request.setAssignmentDurationInSeconds(600L);
        // Reward is a USD dollar amount - USD$0.20 in the example below
        request.setReward("0.20");
        request.setTitle("Determine if tweets contain COVID misinformation");
        request.setKeywords("covid, research, twitter");
        request.setDescription("Indicate whether the specified tweet contains misinformation about COVID-19.");
        request.setQuestion(questionXml);
        request.setQualificationRequirements(Collections.singletonList(localeRequirement));

        CreateHITResult result = client.createHIT(request);
        return new HITInfo(result.getHIT().getHITId(), result.getHIT().getHITTypeId());
    }
}
