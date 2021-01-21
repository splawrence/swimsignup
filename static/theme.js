$(document).ready(function() {
   var table = $('#eventsTable').DataTable( {
        select: true
    } );

    var selectedEventList = []
    $('#btnRegister').click(function () {
        let rows = table.rows('.selected');
        if(rows.data().length > 0 ) {
            rows.every(function(rowIdx, tableLoop, rowLoop){
                var event = this.data();
                selectedEventList.push("[" + event + "]");
            });
            $('#eventList').val(selectedEventList);
        }
    })
} );