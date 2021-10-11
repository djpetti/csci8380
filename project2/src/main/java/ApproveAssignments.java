/*
 * Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
 * with the License. A copy of the License is located at
 *
 * http://aws.amazon.com/apache2.0/
 *
 * or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
 * OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions
 * and limitations under the License.
 */
import java.io.IOException;
import java.util.Collections;
import java.util.List;

import com.amazonaws.client.builder.AwsClientBuilder.EndpointConfiguration;
import com.amazonaws.services.mturk.AmazonMTurk;
import com.amazonaws.services.mturk.AmazonMTurkClientBuilder;
import com.amazonaws.services.mturk.model.ApproveAssignmentRequest;
import com.amazonaws.services.mturk.model.Assignment;
import com.amazonaws.services.mturk.model.AssignmentStatus;
import com.amazonaws.services.mturk.model.GetHITRequest;
import com.amazonaws.services.mturk.model.GetHITResult;
import com.amazonaws.services.mturk.model.ListAssignmentsForHITRequest;
import com.amazonaws.services.mturk.model.ListAssignmentsForHITResult;

/*
 * Before connecting to MTurk, set up your AWS account and IAM settings as described here:
 * https://blog.mturk.com/how-to-use-iam-to-control-api-access-to-your-mturk-account-76fe2c2e66e2
 *
 * Configure your AWS credentials as described here:
 * http://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/credentials.html
 *
 */

public class ApproveAssignments {

    // TODO Change this to your HIT ID - see CreateHITSample.java for generating a HIT
    private static final String[] HIT_ID_TO_APPROVE = new String[]{
            "3P0I4CQYW7NZBUQ8HKNB5E9DBEOWOP",
            "3W3RSPVVH17ED5Y69SSIV9KMVT8UL7",
            "36U4VBVNRXTPG3TJECPEHLTL1LXRUU",
            "3ZLW647WBUBODPZFK2ECT4VDCGY23J",
            "3R16PJFTTC74C1M99MPZ359D7GG4KS",
            "3XEIP58NM93VZ4SGFFRQC1Z1XBNZL1",
            "3WKGUBL7T82FW74RUM10I5MSWGL4LV",
            "3FDWKV9VDWIYJNGR94TXVMZBVYYUM9",
            "3HEADTGN3Y8PTIIJJ2ZJD7V4FS6RVJ",
            "3FULMHZ7P3DZ2PMCUY2FII1HWLB4MX",
            "3GONHBMNI4EF5MA1FRS5CEEQXGDZM3",
            "3PZDSVZ3KEX5K77C6ZHFVXQH1BL4NX",
            "3PIOQ99R8724151RL58X81OB0O8UN9",
            "3UAU495MJR8MJQ13MK8ANQOGQYDUOO",
            "31KSVEGZ4D8287IO9C4FZ9EIM18RWT",
            "3ODOP6T3B109VLIJKGJV39NJQGU244",
            "3G57RS03IQLRR4MJYL2581TXQCP259",
            "3NKW03WTMVN2W63OWXFFUJ4DQF6WQX",
            "372AGES0JDLHX7NEJH011SSPV3ERXM",
            "3URJ6VVYVY3N2S7O7EHSAMQMRLQ4OC",
            "3QTFNPMJDFYLN4V1RS75PT3Q26NZN3",
            "3MXX6RQ9F4L5NSJPMEU7ZMVC1QM4PT",
            "31KSVEGZ4D8287IO9C4FZ9EIM18WRY",
            "3MG8450X3XQ44QD41KLPCQT6039UP5",
            "3PKVGQTFJQ06XCDOODM3K6ZYX98RYS",
            "3SU800BH9F8P42EJ1X0ECVJG5ZVUQW",
            "36QZ6V159IT1HITWT1PJ7VYHNNGUSL",
            "375VSR8FW5P622NTKZOMYD8033CRZJ",
            "3SBX2M1TLM3QN4K4MR9WZRLM6M84QK",
            "38O9DZ0A7B3NA8MX34CA077XM7026P"};

    private static final String SANDBOX_ENDPOINT = "mturk-requester-sandbox.us-east-1.amazonaws.com";
    private static final String SIGNING_REGION = "us-east-1";

    public static void main(final String[] argv) throws IOException {
        final ApproveAssignments sandboxApp = new ApproveAssignments(getSandboxClient());
        for (String id: HIT_ID_TO_APPROVE)
            sandboxApp.approveAssignment(id);
    }

    private final AmazonMTurk client;

    private ApproveAssignments(final AmazonMTurk client) {
        this.client = client;
    }

    /*
    Use the Amazon Mechanical Turk Sandbox to publish test Human Intelligence Tasks (HITs) without paying any money.
    Make sure to sign up for a Sanbox account at https://requestersandbox.mturk.com/ with the same credentials as your main MTurk account.
    */
    private static AmazonMTurk getSandboxClient() {
        AmazonMTurkClientBuilder builder = AmazonMTurkClientBuilder.standard();
        builder.setEndpointConfiguration(new EndpointConfiguration(SANDBOX_ENDPOINT, SIGNING_REGION));
        return builder.build();
    }

    private void approveAssignment(final String hitId) {
        GetHITRequest getHITRequest = new GetHITRequest();
        getHITRequest.setHITId(hitId);
        GetHITResult getHITResult = client.getHIT(getHITRequest);
        System.out.println("HIT " + hitId + " status: " + getHITResult.getHIT().getHITStatus());

        ListAssignmentsForHITRequest listHITRequest = new ListAssignmentsForHITRequest();
        listHITRequest.setHITId(hitId);
        listHITRequest.setAssignmentStatuses(Collections.singletonList(AssignmentStatus.Submitted.name()));

        // Get a maximum of 10 completed assignments for this HIT
        listHITRequest.setMaxResults(10);
        ListAssignmentsForHITResult listHITResult = client.listAssignmentsForHIT(listHITRequest);
        List<Assignment> assignmentList = listHITResult.getAssignments();
        System.out.println("The number of submitted assignments is " + assignmentList.size());

        // Iterate through all the assignments received
        for (Assignment asn : assignmentList) {
            System.out.println("The worker with ID " + asn.getWorkerId() + " submitted assignment "
                    + asn.getAssignmentId() + " and gave the answer " + asn.getAnswer());

            // Approve the assignment
            ApproveAssignmentRequest approveRequest = new ApproveAssignmentRequest();
            approveRequest.setAssignmentId(asn.getAssignmentId());
            approveRequest.setRequesterFeedback("Good work, thank you!");
            approveRequest.setOverrideRejection(false);
            client.approveAssignment(approveRequest);
            System.out.println("Assignment has been approved: " + asn.getAssignmentId());
        }
    }
}