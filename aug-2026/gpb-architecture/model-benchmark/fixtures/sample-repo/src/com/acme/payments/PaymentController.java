package com.acme.payments;

// Fixture corpus for the model-benchmark skill. Deliberately small and
// deliberately flawed: the defects here are the oracle for the bundled suites.
public class PaymentController {

    private final PaymentService paymentService;

    public PaymentController(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    public ChargeResponse createCharge(ChargeRequest request) {
        return paymentService.charge(request);
    }

    public OrderView search(String query) {
        // SEEDED: query flows straight through to the repository (CWE-89 source)
        return orderRepository.findOrders(query);
    }

    private OrderRepository orderRepository;
}
