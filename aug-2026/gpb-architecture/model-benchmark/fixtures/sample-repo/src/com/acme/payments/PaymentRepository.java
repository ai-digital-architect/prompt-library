package com.acme.payments;

public class PaymentRepository {
    public void save(ChargeResponse response) {
        jdbc.execute("INSERT INTO payments VALUES (?)", response.id());
    }
    private Jdbc jdbc;
}
