this.logger.info("script oid"+this.obj.oid);
var string = this.omf.getString(this.obj.oid, 'Script', 'scriptFile');
var base64 = Java.type('java.util.Base64');
var base64n = Java.type('org.apache.commons.codec.binary.Base64');
var JString = Java.type('java.lang.String')
var destring = new JString(base64.getDecoder().decode(string.toString()));
this.logger.info('finish get file content'+string.toString());
this.logger.info('content'+destring);
this.omf.edit({"oid": this.obj.oid, "scriptContent": destring}, "Script");