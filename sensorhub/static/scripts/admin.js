"use strict";

const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

function renderMsg(msg) {
    $("div.notification").html("<p class='msg'>" + msg + "</p>");
}

function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

function sendData(href, method, item, postProcessor) {
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
}

function sensorRow(item) {
    let link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderSensor)'>show</a>";

    return "<tr><td>" + item.name +
            "</td><td>" + item.model +
            "</td><td>" + item.location +
            "</td><td>" + link + "</td></tr>";
}

function measurementRow(item) {
    return "<tr><td>" + item.time + "</td><td>" + item.value + "</td></tr>";
}

function appendSensorRow(body) {
    $(".resulttable tbody").append(sensorRow(body));
}

function getSubmittedSensor(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendSensorRow);
    }
}

function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

function submitSensor(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.name = $("input[name='name']").val();
    data.model = $("input[name='model']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedSensor);
}

function renderSensorForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.schema.properties.name;
    let model = ctrl.schema.properties.model;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitSensor);
    form.append("<label>" + name.description + "</label>");
    form.append("<input type='text' name='name'>");
    form.append("<label>" + model.description + "</label>");
    form.append("<input type='text' name='model'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function renderSensor(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].collection.href +
        "' onClick='followLink(event, this, renderSensors)'>collection</a> | " +
        "<a href='" +
        body["@controls"]["senhub:measurements-first"].href.replace("{index}", "0") +
        "' onClick='followLink(event, this, renderMeasurements)'>measurements</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    renderSensorForm(body["@controls"].edit);
    $("input[name='name']").val(body.name);
    $("input[name='model']").val(body.model);
    $("form input[type='submit']").before(
        "<label>Location</label>" +
        "<input type='text' name='location' value='" +
        body.location + "' readonly>"
    );
}

function renderMeasurements(body) {
    let tablectrl = $("div.tablecontrols");
    tablectrl.empty();
    let prev = body["@controls"].prev;
    let next = body["@controls"].next;
    if (prev) {
        tablectrl.append(
            "<a href='" + prev.href +
            "' onClick='followLink(event, this, renderMeasurements)'>prev</a>"
        );
    }
    if (prev && next) {
        tablectrl.append(" | ");
    }
    if (next) {
        tablectrl.append(
            "<a href='" + next.href +
            "' onClick='followLink(event, this, renderMeasurements)'>next</a>"
        );
    }
    $(".resulttable thead").html(
        "<tr><th>Time</th><th>Value</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(measurementRow(item));
    });
}

function renderSensors(body) {
    $("div.navigation").empty();
    $(".resulttable thead").html(
        "<tr><th>Name</th><th>Model</th><th>Location</th><th>Actions</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(sensorRow(item));
    });
    renderSensorForm(body["@controls"]["senhub:add-sensor"]);
}

$(document).ready(function () {
    getResource("http://localhost:5000/api/sensors/", renderSensors);
});






/*function renderHeaders(first_item) {
    let headers = Object.keys(first_item).filter((key) => !key.startsWith("@"));
    let tr = $("<tr>");
    headers.forEach(function (header) {
        tr.append("<th>" + header + "</th>");
    });
    $(".resulttable thead").append(tr);
    return headers;
}

function renderCollection(body) {
    let first = body.items[0];
    if (first === undefined) {
        $("div.error").html("<p>No data to show</p>");
        return;
    }
    let headers = renderHeaders(first);
    let tbody = $(".resulttable tbody");
    body.items.forEach(function (item) {
        let tr = $("<tr>");
        let cells = headers.map((key) => "<td>" + item[key] + "</td>");
        tr.append(cells);
        tbody.append(tr);
    });
}*/