package com.acme.payments;

public class OrderRepository {

    private Jdbc jdbc;

    public OrderView findOrders(String query) {
        // SEEDED DEFECT: CWE-89. String concatenation into a SQL statement,
        // reachable from PaymentController.search with attacker-controlled input.
        String sql = "SELECT * FROM orders WHERE customer_name = '" + query + "'";
        return jdbc.execute(sql);
    }
}
