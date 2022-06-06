import re
import yaml
import os
import errno
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Utils:
    def parse_response(self, response, pattern):
        return re.compile(pattern, re.DOTALL).search(response).group(1)

    def get_conf(self, file):
        with open(file, "r") as f:
            return yaml.safe_load(f)

    def file_lines_to_array(self, conf_file):
        arr = []
        with open(conf_file) as conf:
            for line in (
                line
                for line in conf
                if not line.startswith("#") and line.strip()
            ):
                arr.append(line.strip())
        return arr

    def metric_persistence(
        self,
        plugin_name,
        metric_nature,
        vpn_name,
        q_name,
        client_username,
        metric_name,
        metric_value,
        persistence_location,
    ):
        to_be_sent = True
        t_metric = 0
        self.create_dir(
            persistence_location,
            plugin_name + "/" + metric_nature + "/" + vpn_name + "/" + q_name,
        )
        doc = {}
        try:
            # YAML exist
            with open(
                persistence_location
                + "/"
                + plugin_name
                + "/"
                + metric_nature
                + "/"
                + vpn_name
                + "/"
                + q_name
                + "/"
                + client_username
                + ".yaml",
                "r",
            ) as f:
                doc = yaml.safe_load(f)
            t_metric = int(metric_value) - int(doc[metric_name])
            # In case there is stats reinit data could be negative
            if t_metric < 0:
                to_be_sent = False
            doc[metric_name] = metric_value
            with open(
                persistence_location
                + "/"
                + plugin_name
                + "/"
                + metric_nature
                + "/"
                + vpn_name
                + "/"
                + q_name
                + "/"
                + client_username
                + ".yaml",
                "w",
            ) as f:
                yaml.dump(doc, f)
        except Exception:
            # YAML don't exist
            # self.logger.debug("Exception occured !")
            to_be_sent = False
            doc[metric_name] = metric_value
            with open(
                persistence_location
                + "/"
                + plugin_name
                + "/"
                + metric_nature
                + "/"
                + vpn_name
                + "/"
                + q_name
                + "/"
                + client_username
                + ".yaml",
                "w",
            ) as f:
                yaml.dump(doc, f)
        return to_be_sent, t_metric

    def create_dir(self, path, folder_name):
        try:
            os.makedirs(path + "/" + folder_name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def del_non_number_json_element(self, json_obj):
        if json_obj:
            res = {}
            for key, value in json_obj.items():
                try:
                    if value:
                        float(value)
                        res[key] = value
                except Exception:
                    pass
            return res

    def same_lvl_json(self, json_obj, json_out, json_obj_header, prefix):
        if json_obj:
            for json_key in json_obj.keys():
                if type(json_obj[json_key]) != dict:
                    if prefix != "":
                        json_out[prefix + "-" +
                                 json_key] = json_obj.get(json_key)
                    #elif json_obj_header != "":
                    #    # in case we want to include the parent
                    #    json_out[json_obj_header] = json_obj.get(json_key)
                    else:
                        json_out[json_key] = json_obj.get(json_key)
                else:
                    # used to recurse on json objects
                    json_out = self.same_lvl_json(
                        json_obj[json_key], json_out, json_key, prefix
                    )
        return json_out

    def json_fields_selector(self, json_obj, json_out, fields_selector_array):
        for json_key in json_obj.keys():
            if json_key in fields_selector_array:
                json_out[json_key] = json_obj[json_key]
        return json_out

    def sum_if_exist(self, obj_list):
        metric_dic = {}
        i = 1
        for item in obj_list:
            while i < len(item):
                new_metric_key = (
                    list(item.values())[0] + ":" + list(item.keys())[i]
                )
                client_instances_count = (
                    list(item.values())[0] + ":client-instances-count"
                )
                metric_dic[new_metric_key] = metric_dic.get(
                    new_metric_key, 0
                ) + int(list(item.values())[i])
                i += 1
            metric_dic[client_instances_count] = (
                metric_dic.get(client_instances_count, 0) + 1
            )
            i = 1
        return metric_dic

    def set_logger(self, log_lvl, instance_name):
        if log_lvl.upper() == "DEBUG":
            log_lvl = logging.DEBUG
        elif log_lvl.upper() == "INFO":
            log_lvl = logging.INFO
        elif log_lvl.upper() == "WARNING":
            log_lvl = logging.WARNING
        elif log_lvl.upper() == "ERROR":
            log_lvl = logging.ERROR

        # create logger with 'main'
        logger = logging.getLogger(instance_name)
        logger.setLevel(log_lvl)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(log_lvl)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger

    def get_sia_irn(self, client_username):
        # GFE awgfe07 (IRN-67490)
        sia_irn = client_username.split(" ")
        if len(sia_irn) == 3:
            return sia_irn[0], sia_irn[2][1:-1]
        else:
            return "N/A", "N/A"
