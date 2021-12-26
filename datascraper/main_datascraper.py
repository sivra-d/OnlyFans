import os
import timeit
from typing import Any, Optional

import helpers.main_helper as main_helper
import modules.fansly as m_fansly
import modules.onlyfans as m_onlyfans
import modules.starsavn as m_starsavn
from apis.fansly import fansly as Fansly
from apis.onlyfans import onlyfans as OnlyFans
from apis.starsavn import starsavn as StarsAVN
from helpers.main_helper import choose_option

api_helper = OnlyFans.api_helper


async def start_datascraper(
    json_config: dict[Any, Any],
    site_name_lower: str,
    api: Optional[OnlyFans.start | Fansly.start | StarsAVN.start] = None,
    webhooks: bool = True,
) -> Optional[OnlyFans.start]:
    json_settings = json_config["settings"]
    json_sites = json_config["supported"]
    main_helper.assign_vars(json_config)

    json_site_settings = json_sites[site_name_lower]["settings"]

    auto_model_choice = json_site_settings["auto_model_choice"]
    if isinstance(auto_model_choice, str):
        temp_identifiers = auto_model_choice.split(",")
        identifiers = [x for x in temp_identifiers if x]
    else:
        identifiers = []
    auto_profile_choice = json_site_settings["auto_profile_choice"]
    subscription_array = []
    proxies: list[str] = await api_helper.test_proxies(json_settings["proxies"])
    if json_settings["proxies"] and not proxies:
        print("Unable to create session")
        return None
    archive_time = timeit.default_timer()
    match site_name_lower:
        case "onlyfans":
            site_name = "OnlyFans"
            module = m_onlyfans
            if not api:
                api = OnlyFans.start(max_threads=json_settings["max_threads"])
                api.settings = json_config
                api = main_helper.process_profiles(
                    json_settings, proxies, site_name, api
                )
                print

            subscription_array = []
            auth_count = 0
            jobs = json_site_settings["jobs"]
            subscription_list = module.format_options(api.auths, "users")
            if not auto_profile_choice:
                print("Choose Profile")
            auths = choose_option(subscription_list, auto_profile_choice, True)
            api.auths = [x.pop(0) for x in auths]
            for auth in api.auths:
                if not auth.auth_details:
                    continue
                module.assign_vars(
                    auth.auth_details, json_config, json_site_settings, site_name
                )
                setup = False
                setup, subscriptions = await module.account_setup(
                    auth, identifiers, jobs, auth_count
                )
                if not setup:
                    if webhooks:
                        await main_helper.process_webhooks(
                            api, "auth_webhook", "failed"
                        )
                    auth_details = {}
                    auth_details["auth"] = auth.auth_details.export()
                    profile_directory = auth.profile_directory
                    if profile_directory:
                        user_auth_filepath = os.path.join(
                            auth.profile_directory, "auth.json"
                        )
                        main_helper.export_data(auth_details, user_auth_filepath)
                    continue
                auth_count += 1
                subscription_array += subscriptions
                await main_helper.process_webhooks(api, "auth_webhook", "succeeded")
                # Do stuff with authed user
            subscription_list = module.format_options(
                subscription_array, "usernames", api.auths
            )
            if jobs["scrape_paid_content"] and api.has_active_auths():
                print("Scraping Paid Content")
                await module.paid_content_scraper(api, identifiers)
            if jobs["scrape_names"] and api.has_active_auths():
                print("Scraping Subscriptions")
                await main_helper.process_names(
                    module,
                    subscription_list,
                    auto_model_choice,
                    api,
                    json_config,
                    site_name_lower,
                    site_name,
                )
            await main_helper.process_downloads(api, module)
            if webhooks:
                await main_helper.process_webhooks(api, "download_webhook", "succeeded")
        case "fansly":
            site_name = "Fansly"
            module = m_fansly
            if not api:
                api = Fansly.start(max_threads=json_settings["max_threads"])
                api.settings = json_config
                api = main_helper.process_profiles(
                    json_settings, proxies, site_name, api
                )

            subscription_array = []
            auth_count = 0
            jobs = json_site_settings["jobs"]
            subscription_list = module.format_options(api.auths, "users")
            if not auto_profile_choice:
                print("Choose Profile")
            auths = choose_option(subscription_list, auto_profile_choice, True)
            api.auths = [x.pop(0) for x in auths]
            for auth in api.auths:
                if not auth.auth_details:
                    continue
                module.assign_vars(
                    auth.auth_details, json_config, json_site_settings, site_name
                )
                setup = False
                setup, subscriptions = await module.account_setup(
                    auth, identifiers, jobs, auth_count
                )
                if not setup:
                    if webhooks:
                        await main_helper.process_webhooks(
                            api, "auth_webhook", "failed"
                        )
                    auth_details = {}
                    auth_details["auth"] = auth.auth_details.export()
                    profile_directory = auth.profile_directory
                    if profile_directory:
                        user_auth_filepath = os.path.join(
                            auth.profile_directory, "auth.json"
                        )
                        main_helper.export_data(auth_details, user_auth_filepath)
                    continue
                auth_count += 1
                subscription_array += subscriptions
                await main_helper.process_webhooks(api, "auth_webhook", "succeeded")
                # Do stuff with authed user
            subscription_list = module.format_options(
                subscription_array, "usernames", api.auths
            )
            if jobs["scrape_paid_content"] and api.has_active_auths():
                print("Scraping Paid Content")
                # await module.paid_content_scraper(api, identifiers)
            if jobs["scrape_names"] and api.has_active_auths():
                print("Scraping Subscriptions")
                await main_helper.process_names(
                    module,
                    subscription_list,
                    auto_model_choice,
                    api,
                    json_config,
                    site_name_lower,
                    site_name,
                )
            await main_helper.process_downloads(api, module)
            if webhooks:
                await main_helper.process_webhooks(api, "download_webhook", "succeeded")
        case "starsavn":
            site_name = "StarsAVN"
            module = m_starsavn
            if not api:
                api = StarsAVN.start(max_threads=json_settings["max_threads"])
                api.settings = json_config
                api = main_helper.process_profiles(
                    json_settings, proxies, site_name, api
                )
                print

            subscription_array = []
            auth_count = 0
            jobs = json_site_settings["jobs"]
            subscription_list = module.format_options(api.auths, "users")
            if not auto_profile_choice:
                print("Choose Profile")
            auths = choose_option(subscription_list, auto_profile_choice, True)
            api.auths = [x.pop(0) for x in auths]
            for auth in api.auths:
                if not auth.auth_details:
                    continue
                module.assign_vars(
                    auth.auth_details, json_config, json_site_settings, site_name
                )
                setup = False
                setup, subscriptions = await module.account_setup(
                    auth, identifiers, jobs, auth_count
                )
                if not setup:
                    if webhooks:
                        await main_helper.process_webhooks(
                            api, "auth_webhook", "failed"
                        )
                    auth_details = {}
                    auth_details["auth"] = auth.auth_details.export()
                    profile_directory = auth.profile_directory
                    if profile_directory:
                        user_auth_filepath = os.path.join(
                            auth.profile_directory, "auth.json"
                        )
                        main_helper.export_data(auth_details, user_auth_filepath)
                    continue
                auth_count += 1
                subscription_array += subscriptions
                await main_helper.process_webhooks(api, "auth_webhook", "succeeded")
                # Do stuff with authed user
            subscription_list = module.format_options(
                subscription_array, "usernames", api.auths
            )
            if jobs["scrape_paid_content"] and api.has_active_auths():
                print("Scraping Paid Content")
                # await module.paid_content_scraper(api, identifiers)
            if jobs["scrape_names"] and api.has_active_auths():
                print("Scraping Subscriptions")
                await main_helper.process_names(
                    module,
                    subscription_list,
                    auto_model_choice,
                    api,
                    json_config,
                    site_name_lower,
                    site_name,
                )
            await main_helper.process_downloads(api, module)
            if webhooks:
                await main_helper.process_webhooks(api, "download_webhook", "succeeded")
    stop_time = str(int(timeit.default_timer() - archive_time) / 60)[:4]
    print("Archive Completed in " + stop_time + " Minutes")
    return api
