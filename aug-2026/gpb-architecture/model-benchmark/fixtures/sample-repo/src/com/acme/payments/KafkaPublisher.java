package com.acme.payments;

public class KafkaPublisher {
    public void publish(ChargeResponse response) {
        producer.send("payments.charged", response);
    }
    private Producer producer;
}
