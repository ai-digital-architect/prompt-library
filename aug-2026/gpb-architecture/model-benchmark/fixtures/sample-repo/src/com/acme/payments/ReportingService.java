package com.acme.payments;

public class ReportingService {
    // SEEDED DEFECT: a bounded-context violation. Reporting reads the payments
    // datastore directly instead of going through PaymentService.
    private PaymentRepository paymentRepository;

    public Report build() {
        return new Report(paymentRepository.findAll());
    }
}
