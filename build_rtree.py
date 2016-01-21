#coding:utf-8
import radix
import cPickle
from query import query_local
import random
from netaddr import IPRange, IPSet

def ip_integer_from_string(s):
    """Convert dotted IPv4 address to integer."""
    return reduce(lambda a,b: a<<8 | b, map(int, s.split(".")))

def ip_integer_to_string(ip):
     """Convert 32-bit integer to dotted IPv4 address."""
     return ".".join(map(lambda n: str(ip>>n & 0xFF), [24,16,8,0]))

if __name__ == '__main__':
    print ip_integer_to_string(0x80000000)

def ip_integer_to_integer_array(ip):
    """convert 32-bit integer to [a, b, c, d]"""
    return map(lambda n: ip>>n & 0xff, [24,16,8,0])

def generate_random_ip(network, masklen):
    random_int = random.randint(0, (1<<(32-masklen)) -1)
    return ip_integer_to_string(ip_integer_from_string(network) + random_int)

def generate_random_ip_splited(network, masklen, splited_num, splited_order):
    splited_size = (1<<(32-masklen))/splited_num
    random_int = random.randint(splited_size*splited_order,splited_size*(splited_order+1) - 1)
    return ip_integer_to_string(ip_integer_from_string(network) + random_int)

def split_network_from_start_to_end(start, end):
    ip = IPRange(start, end)
    return map(lambda net:(str(net.network), net.prefixlen, net.size), ip.cidrs())

class ipRadixDB:
    totalRecords = 0
    recordKeys = ['country', 'city', 'isp', 'ip', 'province']
    def __init__(self, radixFile="radix"):
        try:
            self.radixFile = open(radixFile,"rb")
            self.rtree = cPickle.load(self.radixFile)
        except:
            self.rtree = radix.Radix()
        finally:
            self.previousSinaIpSet = IPSet()
            ipRadixDB.totalRecords = len(self.rtree.prefixes())

    def addPrefix(self, network, masklen):
        self.rnode = self.rtree.add(network, masklen)
        self.rnode.data["ip_amount"] = 1<<(32-masklen)

    def delPrefix(self, network, masklen):
        self.rtree.delete(network, masklen)

    def getNodeUsePrefix(self, network, masklen):
        return self.rtree.search_exact(network, masklen)

    def queryIp(self, ip, masklen=24):
        self.rnode = self.rtree.search_best(ip)
        return self.rnode

    def queryIpWithUpdate(self, ip, masklen=24):
        if not ip in self.previousSinaIpSet:
            self.rnode = self.rtree.search_best(ip)
            if not self.rnode:#this ip is not in the prefix table
                jsonData = query_local(ip)
                if jsonData:
                    start = jsonData.get("start","")
                    if start:#we have the sina data:
                        end = jsonData["end"]
                        iprange = IPRange(start, end)
                        self.previousSinaIpSet = IPSet(iprange.cidrs())
                        for net_tuple in split_network_from_start_to_end(start, end):
                            self.addPrefix(net_tuple[0], net_tuple[1])
                            for k in ipRadixDB.recordKeys:
                                if k == "ip":
                                    self.rnode.data[k] = jsonData.get(k,ip)
                                else:
                                    self.rnode.data[k] = jsonData[k]
                    else:
                        self.addPrefix(ip, masklen)
                        for k in ipRadixDB.recordKeys:
                            self.rnode.data[k] = jsonData[k]
            else:
                if self.rnode.prefixlen < 24 or not self.rnode.data.get("country",""):#only the prefix is bigger than x/24 network
                    jsonData = query_local(ip)#maybe the prefix is too large, we need to substrac the prefix
                    if jsonData:
                        jsonData["ip"] = ip
                        self.substractPrefix(self.rnode, jsonData)

    def substractPrefix(self, rnode, jsonData):
        data = rnode.data
        prefixlen = rnode.prefixlen
        network = rnode.network
        if (jsonData["city"] != data.get("city","") or jsonData["province"] != data.get("province","") or jsonData["isp"] != data.get("isp", "") or jsonData["country"] != data.get("isp", "")):#we got the sina json data
            start = jsonData.get("start", "")
            if start:
                end = jsonData["end"]
                iprange = IPRange(start, end)
                self.previousSinaIpSet = IPSet(iprange.cidrs())
                for net_tuple in split_network_from_start_to_end(start, end):
                    self.rnode = self.rtree.search_exact(net_tuple[0], net_tuple[1])
                    if not self.rnode:#//while we donn't have this node
                        self.addPrefix(net_tuple[0], net_tuple[1])#add this node
                        if (network == net_tuple[0]):#the node we added start from our previous node start point
                            data["ip_amount"] -= net_tuple[2] #we substract a subnetwork form the big network, we need to decrease the ip amount
                        else:
                            ip_remove_amount = min(ip_integer_from_string(network) + (1 << (32 - prefixlen)) - ip_integer_from_string(net_tuple[0]), 1<<(32-net_tuple[1]))
                            if ip_remove_amount > 0:
                                data["ip_amount"] -= ip_remove_amount
                    for k in ipRadixDB.recordKeys:
                        self.rnode.data[k] = jsonData[k]
                if data["ip_amount"] <= 0:#we have divided the big prefix into small piece
                    self.delPrefix(network, prefixlen) #delete big prefix
            else:#we just have taobao's data, just update the node
                for k in ipRadixDB.recordKeys:
                    self.rnode.data[k] = jsonData[k]

    def prefixMerge(self):
        prefix_stack = []
        compare_key = ["country","province","city","isp"]
        for prefix in self.rtree.prefixes():
            data = self.rtree.search_exact(prefix).data
            if len(prefix_stack):
                previous = prefix_stack.pop()
                pdata = self.rtree.search_exact(previous).data
                if reduce(lambda a,b:a*b, [ pdata[k] == data[k] for k in compare_key]) or (data['country'] != u'中国' and data['country'] == pdata['country']):#the new prefix is same as the previous one
                    prefix_stack += [previous, prefix]
                else:#not same, merge all the prefix in the stack
                    if len(prefix_stack) :
                        network_list = IPSet(prefix_stack+[previous]).iter_cidrs()
                        newdata = pdata.copy()
                        for k in prefix_stack:
                            self.rtree.delete(k)
                        self.rtree.delete(previous)
                        #print network_list
                        for k in network_list:
                            node = self.rtree.add(str(k))
                            for key in compare_key:
                                node.data[key] = newdata[key]
                            node.data["ip"] = newdata["ip"]
                            node.data["ip_amount"] = k.size
                        prefix_stack = [prefix]
            else:
                prefix_stack.append(prefix)
        if len(prefix_stack) >= 2:
            previous = prefix_stack.pop()
            pdata = self.rtree.search_exact(previous).data
            newdata = pdata.copy()
            network_list = IPSet(prefix_stack+[previous]).iter_cidrs()
            for k in prefix_stack:
                self.rtree.delete(k)
            self.rtree.delete(previous)
            for k in network_list:
                node = self.rtree.add(str(k))
                for key in compare_key:
                    node.data[key] = newdata[key]
                node.data["ip"] = newdata["ip"]
                node.data["ip_amount"] = k.size


    def saveToFile(self,file="rtree"):
        cPickle.dump(self.rtree, open(file, "wb"), 2)

    def writeRawToFile(self, file="raw_data"):
        data_key = ["country", "province", "city", "isp", "ip", "ip_amount"]
        rawFile = open(file, "wb")
        for node in self.rtree.nodes():
            data = [ node.prefix ] + [ node.data[k] for k in data_key ]
            string = ";".join(map(unicode, data))
            rawFile.write(string.encode("utf-8") + "\n")
        rawFile.close()

    def loadFromRawFile(self, file="raw_data"):
        data_key = ["country", "province", "city", "isp", "ip", "ip_amount"]
        rawFile = open(file, "rb")
        for line in rawFile.readlines():
            items = line.split(";")
            prefix = items[0]
            node = self.rtree.add(prefix)
            for k,v in enumerate(data_key):
                if v == "ip_amount":
                    node.data[v] = int(items[1+k])
                else:
                    node.data[v] = items[1+k].decode("utf-8")
        rawFile.close()
