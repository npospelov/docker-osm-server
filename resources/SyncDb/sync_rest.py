import requests
import configparser
import lxml
import lxml.etree
import os
import subprocess
import logging

class CmdCsList:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.osm_host = None

        try:
            self.config.read('sync_db.ini')
            #print ([x for x in self.config['DEFAULT'].keys()])
            self.osm_host = self.config['DEFAULT'].get('osm_host')
        except:
            logging.error("cannot get 'osm_host' from config")


    def exec(self):
        """
        определить все множество changeset-ов и выбрать последний
        :return:
        """
        cs_list = []
        if self.osm_host is None:
            return None

        url = "http://{0}:3000/api/0.6/changesets".format(self.osm_host)
        resp = requests.get(url)
        cs_list = []
        if resp.status_code == 200:
            tree = None
            try:
                tree = lxml.etree.fromstring(bytes(resp.text,encoding='utf-8'))
            except Exception as e:
                logging.error("Error: cannot parse changeset list due to %s!" % str(e))
                #print (resp.text)
                return None

            cs = tree.xpath("/osm/changeset[@id]")
            for it in cs:
                cs_id = int(it.get('id'))
                cs_list.append(cs_id)

        cs_list.sort()
        return cs_list


class CmdGetChangeset:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.osm_host = None
        self.osc_dir = None

        try:
            self.config.read('sync_db.ini')
            #print ([x for x in self.config['DEFAULT'].keys()])
            self.osm_host = self.config['DEFAULT'].get('osm_host')
            self.osc_dir = self.config['OVERPASS'].get('osc_dir')
        except:
            logging.error("cannot get 'osm_host','osc_dir' from config")

        if not os.path.exists(self.osc_dir):
            os.makedirs(self.osc_dir)
        #self.change_xml_dict = dict()


    def exec(self,cs_num):
        """
        определить XML c заданным в cs_num changeset-ом
        :return:
        """

        if self.osm_host is None:
            logging.error("Error: cannot detect osm_host!")
            return None

        url = "http://{0}:3000/api/0.6/changeset/{1}/download".format(self.osm_host, cs_num)
        resp = requests.get(url)
        if resp.status_code == 200:
            fname ='{0}/{1}.osc'.format(self.osc_dir,cs_num)
            #print ("fname=%s" % fname)

            try:
                ff = open(fname,"wb")
                ff.write(bytes(resp.text,encoding='utf-8'))
                ff.close()
            except Exception as e:
                logging.error("Error: cannot open file %s!" % fname)
                #print (resp.text)
                return None

            return resp.text
        else:
            logging.error("Error: request %s for url=\'%s\'" % (resp.status_code,url))

        return None

    # def mergeXml(self):
    #     res_tree = None
    #     for xkey in self.change_xml_dict.keys():
    #         try:
    #             ctree = lxml.etree.fromstring(bytes(self.change_xml_dict.get(xkey), encoding='utf-8'))
    #             if res_tree is None:
    #                 res_tree = ctree
    #                 continue
    #         except Exception as e:
    #             print("Error: cannot parse changeset list due to %s!" % str(e))
    #             #print (resp.text)
    #             return None
    #
    #         ins_position = res_tree



