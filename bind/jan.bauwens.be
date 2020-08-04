;
; BIND data file for local loopback interface
;
$TTL	604800
@	IN	SOA	jan.bauwens.be. root.bauwens.be (
			      5		; Serial
			 604800		; Refresh
			  86400		; Retry
			2419200		; Expire
			 604800 )	; Negative Cache TTL
;
@	IN	NS	jan.bauwens.be.
@	IN	A	192.168.0.173
transmission IN A 192.168.0.173
sonarr IN A 192.168.0.173
emby IN A 192.168.0.173
couchpotato IN A 192.168.0.173
plex IN A 192.168.0.173
radarr IN A 192.168.0.173
jackett IN A 192.168.0.173
