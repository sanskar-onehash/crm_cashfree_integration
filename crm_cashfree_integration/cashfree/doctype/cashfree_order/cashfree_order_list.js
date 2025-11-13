frappe.listview_settings["Cashfree Order"] = {
  get_indicator: function (doc) {
    if (doc.status === "Success") {
      return [doc.status, "green", "status,=,Success"];
    } else if (doc.status === "Failed") {
      return [doc.status, "red", "status,=,Failed"];
    } else if (doc.status === "User Droped") {
      return [doc.status, "yellow", "status,=,Expired"];
    }
  },
};
