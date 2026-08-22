package com.acme.payments;

public class PaymentClient {

    private final HttpClient httpClient;

    public PaymentClient(HttpClient httpClient) {
        this.httpClient = httpClient;
    }

    public ChargeResponse callGateway(ChargeRequest request) {
        // SEEDED DEFECT: no timeout configured on an external synchronous call,
        // and the retry policy below is unbounded. Two distinct resiliency
        // findings sharing one call site.
        RetryPolicy policy = new RetryPolicy();
        policy.setMaxAttempts(Integer.MAX_VALUE);
        return httpClient.post("https://gateway.example.com/charge", request, policy);
    }
}
