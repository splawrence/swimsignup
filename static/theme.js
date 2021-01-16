$(document).ready(function() {
   var table = $('#eventsTable').DataTable( {
        select: true
    } );

    var selectedUrlList = []
    $('#btnRegister').click(function () {
        let rows = table.rows('.selected');
        if(rows.data().length > 0 ) {
            rows.every(function(rowIdx, tableLoop, rowLoop){
                var url = table.cell(this, 0).data();
         
                selectedUrlList.push(url)
            });
            $('#urlList').val(selectedUrlList)
        }
    })
} );