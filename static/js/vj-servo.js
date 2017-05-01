console.log("Start");
var socket = io.connect('http://' + document.domain + ':' + location.port + '/servo');
var updateTimer = null;

socket.on('connect', function(msg) {
    console.log('[INFO] Socket connected.');
    if (!updateTimer)
        updateTimer = setInterval(getStatus, 500);
});

socket.on('disconnect', function(msg) {
    $('#operationSwitch').prop('disabled', true);
    $('#targetPosition').prop('disabled', true);

    clearInterval(updateTimer);
    updateTimer = null;
});

function sendPosition() {
    console.log('sendPosition, value: ' + $('#targetPosition').val());
    socket.emit('moveTo', $('#targetPosition').val());
}

function sendStop() {
    console.log('sendStop');
    socket.emit('stop');
}

function pullToLeft() {
    socket.emit('pullToLeft');
}

function pullToRight() {
    socket.emit('pullToRight');
}

function sendEnable() {
    console.log('sendEnable');
    socket.emit('enable');
}

function resetCenter() {
    socket.emit('resetCenter');
}

function toCenter() {
    $('#targetPosition').val(512).change();
}

function handleOperationSwitch(cb) {
    if (cb.checked)
        sendEnable();
    else
        sendStop();
}

function getStatus() {
    console.log("Fetching status")
    $.ajax({
        url: 'status',
        accepts: 'json',
        success: setStatus,
        cache: false
    });
}

function setStatus(data) {
    console.log(data);

    // Set mode
    cb = $('#operationSwitch');
    cb.prop('checked', data.enabled);
    cb.prop('disabled', false);

    // Set target position
    pos = $('#targetPosition');
    pos.val(data.target_position);
    pos.prop('disabled', false);

    // Set current position
    cur_pos = $('#currentPosition');
    console.log("Setting val to " + data.current_poti_position + data.current_offset);
    cur_pos.val(data.current_poti_position + data.current_offset);
}
