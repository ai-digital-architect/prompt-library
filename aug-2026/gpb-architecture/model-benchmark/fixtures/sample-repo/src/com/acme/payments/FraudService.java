package com.acme.payments;

public class FraudService {
    public void assess(ChargeRequest request) {
        riskEngine.score(request);
    }
    private RiskEngine riskEngine;
}
