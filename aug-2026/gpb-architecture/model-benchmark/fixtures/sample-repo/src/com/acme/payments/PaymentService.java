package com.acme.payments;

public class PaymentService {

    private final PaymentRepository paymentRepository;
    private final FraudService fraudService;
    private final KafkaPublisher kafkaPublisher;
    private final PaymentClient paymentClient;

    public ChargeResponse charge(ChargeRequest request) {
        fraudService.assess(request);
        ChargeResponse response = paymentClient.callGateway(request);
        paymentRepository.save(response);
        kafkaPublisher.publish(response);
        return response;
    }
}
