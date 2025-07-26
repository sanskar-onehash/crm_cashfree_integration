// Copyright (c) 2025, OneHash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cashfree Integration", {
  setup: function (frm) {
    frm.trigger("setup_help");
  },
  setup_help(frm) {
    frm.get_field("help_html").html(`
<h1>💳 Cashfree Payment Integration (JavaScript)</h1>

<p>This script enables payment collection through Cashfree mode. It covers:</p>

<ul>
  <li>Order creation</li>
  <li>Dynamically loading the Cashfree SDK</li>
  <li>Launching the Cashfree payment modal</li>
  <li>Handling different payment result scenarios</li>
</ul>

<hr/>

<h2>📥 Function Parameters</h2>

<h3><code>collectPayment(...)</code> & <code>createCashfreeOrder(...)</code></h3>

<table>
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Type</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>orderCurrency</code></td>
      <td><code>string</code></td>
      <td>Currency code (e.g., <code>"INR"</code>)</td>
    </tr>
    <tr>
      <td><code>orderAmount</code></td>
      <td><code>number</code></td>
      <td>The amount to be charged</td>
    </tr>
    <tr>
      <td><code>customerDetails</code></td>
      <td><code>object</code></td>
      <td>Customer info as expected by Cashfree</td>
    </tr>
    <tr>
      <td><code>orderInvoices</code></td>
      <td><code>array</code></td>
      <td>List of invoices to be linked to the payment</td>
    </tr>
    <tr>
      <td><code>orderMeta</code></td>
      <td><code>object</code></td>
      <td>Extra metadata sent to Cashfree</td>
    </tr>
    <tr>
      <td><code>orderExpiryTime</code></td>
      <td><code>string | number</code></td>
      <td>Optional expiry for the payment session</td>
    </tr>
    <tr>
      <td><code>loadCashfree</code></td>
      <td><code>boolean</code></td>
      <td>Whether to load the SDK dynamically (default: <code>true</code>)</td>
    </tr>
  </tbody>
</table>

<hr/>

<h2>🧾 <code>orderInvoices</code> Format</h2>

<pre><code>[
  {
    invoice_type: "Invoice DocType", // e.g., "Sales Invoice"
    invoice_id: "SINV-0001"          // Actual invoice name
  },
  ...
]
</code></pre>

<hr/>

<h2>📚 Reference for <code>customerDetails</code> and <code>orderMeta</code></h2>

<p>For complete details on structure, required fields, and examples, refer to:</p>

<p>👉🔗 <a href="https://www.cashfree.com/docs/api-reference/payments/latest/orders/create#body-customer-details" target="_blank">Cashfree Orders API Documentation – Customer Details</a></p>

<hr/>

<h2>📄 Full Code</h2>

<p><pre><code>async function collectPayment(
  orderCurrency,
  orderAmount,
  customerDetails,
  orderInvoices,
  orderMeta,
  orderExpiryTime,
  loadCashfree = true,
) {
  const cashfreeOrder = await createCashfreeOrder(
    orderCurrency,
    orderAmount,
    customerDetails,
    orderInvoices,
    orderMeta,
    orderExpiryTime,
    loadCashfree,
  );
  const cashfree = Cashfree({
    mode: "sandbox",
  });
  const checkoutOptions = {
    paymentSessionId: cashfreeOrder.payment_session_id,
    redirectTarget: "_modal",
  };
  cashfree.checkout(checkoutOptions).then((result) => {
    if (result.error) {
      console.log(
        "User has closed the popup or there is some payment error, Check for Payment Status",
      );
      console.log(result.error);
    }
    if (result.redirect) {
      console.log("Payment will be redirected");
    }
    if (result.paymentDetails) {
      console.log("Payment has been completed, Check for Payment Status");
      console.log(result.paymentDetails.paymentMessage);
    }
  });
}

async function createCashfreeOrder(
  orderCurrency,
  orderAmount,
  customerDetails,
  orderInvoices,
  orderMeta,
  orderExpiryTime,
  loadCashfree = true,
) {
  return new Promise((resolve, reject) => {
    frappe.call({
      method:
        "crm_cashfree_integration.cashfree.doctype.cashfree_order.cashfree_order.create_order",
      args: {
        order_currency: orderCurrency,
        order_amount: orderAmount,
        customer_details: customerDetails,
        invoices: orderInvoices,
        order_meta: orderMeta,
        order_expiry_time: orderExpiryTime,
      },
      callback: async function (res) {
        if (res.message && res.message.payment_session_id) {
          if (loadCashfree && !window.Cashfree) {
            await loadExternalScript(res.message.client_script_src);
          }
          resolve(res.message);
        } else {
          reject(\`Order creation failed. \${res}\`);
        }
      },
    });
  });
}

function loadExternalScript(scriptSrc) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = scriptSrc;
    script.onload = function () {
      console.log("loaded");
      resolve();
    };
    script.onerror = function () {
      reject(\`Failed to load the external script: \${scriptSrc}\`);
    };
    document.head.appendChild(script);
  });
}
</code></pre></p>
`);
  },
});
