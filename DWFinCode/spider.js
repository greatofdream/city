// update the city
var grid = this.getAddinById("Grid1");
var query = {
    condition: "and obj.cityOid='"+this.obj.param3+"'"
};
console.log('req conditon'+JSON.stringify(query))
this.dwf_axios.post("/omf/entities/Data/objects", query).then(rsp => {
    if(rsp.data.code != 200){
        console.log('failed get data')
    }else{
        console.log('set data')
        grid.setRowData(rsp.data.data)
    }
});

// update the attribute
var citySelect = this.getAddinById("SingleObjectSelector1");
var cityOid = this.obj.param3
var attrSelect = this.getAddinById("SingleObjectSelector3");
var target= attrSelect.getSelected();

console.log('target')
console.log(target);

var grid = this.getAddinById("Grid1");
console.log(grid.args.columnDefs)
grid.setColumnDefs([])
var defaultColumnDefs = grid.args.columnDefs;
var defaultColLength = 2;//defaultColumnDefs.length;
console.log('defaultCol'+defaultColLength)
console.log(defaultColumnDefs)

var modifyColDefs = [];

    modifyColDefs[0] = defaultColumnDefs[0];//grid.getDefaultColumnDefs();
    modifyColDefs[1] = defaultColumnDefs[1];
    console.log('modifyCol')
    console.log(modifyColDefs)

console.log('begin modify the column')
for (let i=0;i<target.length;i++){
    console.log(target[i].SubIndiName)
    console.log(i+defaultColLength)
    modifyColDefs[i+defaultColLength] = grid.getDefaultColumnDef({
        alignCode: 1,
        attrName: target[i].SubIndiName,
        editable: false,
        colId: target[i].SubIndiName,
        enableFilter: true,
        enableSorting: true,
        field: target[i].SubIndiName,
        headerName: target[i].ChineseName
    });
}
grid.setColumnDefs(modifyColDefs);

console.log('modify defaultCol'+modifyColDefs);
var modReq = {
    condition: "and obj.cityOid='"+cityOid+"'"
};
console.log('req conditon'+JSON.stringify(modReq))
this.dwf_axios.post("/omf/entities/Data/objects", modReq).then(rsp => {
    if(rsp.data.code != 200){
        console.log('failed get data')
    }else{
        console.log('set data')
        grid.setRowData(rsp.data.data)
    }
});
//grid.freshData();
