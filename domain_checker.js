const fs = require('fs');
const dns = require('dns');

// Load domains from domains.json
const domains = JSON.parse(fs.readFileSync('domains.json', 'utf8'));

// ISP DNS List (example DNS servers)
const ISP_DNS_LIST = ['8.8.8.8', '8.8.4.4', '1.1.1.1'];

// Blocked IPs list (example blocked IPs)
const block_ips = ['192.0.2.1', '203.0.113.1', '198.51.100.1', '142.250.207.174', '192.178.211.100'];

async function checkDomain(domain) {
    return new Promise((resolve, reject) => {
        // Use the first DNS server from ISP_DNS_LIST
        const resolver = new dns.Resolver();
        resolver.setServers([ISP_DNS_LIST[0]]);

        resolver.resolve4(domain, (err, addresses) => {
            if (err) {
                console.log(`Error resolving ${domain}: ${err.message}`);
                resolve(null);
                return;
            }

            const ip = addresses[0];
            console.log(`Domain: ${domain}, IP: ${ip}`);

            if (block_ips.includes(ip)) {
                console.log(`NOTICE: Domain ${domain} is blocked (IP: ${ip})`);
            } else {
                console.log(`Domain ${domain} is not blocked`);
            }

            resolve(ip);
        });
    });
}

async function main() {
    console.log('Starting domain checker bot...');

    for (const domain of domains) {
        await checkDomain(domain);
        // Add delay to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    console.log('Domain checking completed.');
}

main().catch(console.error);
