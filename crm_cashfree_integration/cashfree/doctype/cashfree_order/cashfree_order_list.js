frappe.listview_settings["Cashfree Order"] = {
  get_indicator: function (doc) {
    if (doc.payment_status === "Success") {
      return [doc.payment_status, "green", "status,=,Success"];
    } else if (doc.payment_status === "Failed") {
      return [doc.payment_status, "red", "status,=,Failed"];
    } else if (doc.payment_status === "User Droped") {
      return [doc.payment_status, "yellow", "status,=,Expired"];
    }
  },
};
